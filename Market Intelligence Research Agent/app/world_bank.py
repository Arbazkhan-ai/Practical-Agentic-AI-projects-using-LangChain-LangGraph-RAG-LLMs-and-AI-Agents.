"""
Live World Bank API Connector:
Fetches authoritative macroeconomic, tourism, and agricultural indicators for Caribbean markets.
"""

import uuid
import re
from typing import List, Dict, Any, Tuple
import requests
from schemas import ResearchPlan, SourceRecord, SourceContentRecord
from config import WORLD_BANK_INDICATORS, WB_SUPPORTED_ISO, DEFAULT_CARIBBEAN_MARKETS


def resolve_wb_country_codes(plan: ResearchPlan) -> List[str]:
    """
    Extracts relevant ISO3 country codes for World Bank API queries based on research plan markets.
    """
    iso_codes = []
    market_iso_map = {m["market"].lower(): m["iso_code"] for m in DEFAULT_CARIBBEAN_MARKETS}

    if plan.markets:
        for pm in plan.markets:
            pm_lower = pm.lower()
            for m_name, iso in market_iso_map.items():
                if m_name in pm_lower or pm_lower in m_name:
                    if iso in WB_SUPPORTED_ISO:
                        iso_codes.append(iso)

    # Fallback to key representative regional Caribbean economies
    if not iso_codes:
        iso_codes = ["JAM", "BHS", "BRB", "DOM", "LCA", "TTO", "ATG", "GRD"]

    return sorted(list(set(iso_codes)))[:15]


def fetch_world_bank_data(
    plan: ResearchPlan,
    run_id: str,
    project_id: str
) -> Tuple[List[SourceRecord], List[SourceContentRecord]]:
    """
    Queries the World Bank indicator API for all target Caribbean countries.
    Returns generated SourceRecords and SourceContentRecords with structured observations.
    """
    iso_codes = resolve_wb_country_codes(plan)
    if not iso_codes:
        return [], []

    # Parse date range
    date_match = re.findall(r"\b(19\d\d|20\d\d)\b", plan.date_range or "")
    if len(date_match) >= 2:
        start_year, end_year = min(date_match), max(date_match)
    else:
        start_year, end_year = "2015", "2024"

    country_path = ";".join(iso_codes)
    sources: List[SourceRecord] = []
    contents: List[SourceContentRecord] = []

    for ind in WORLD_BANK_INDICATORS:
        ind_code = ind["code"]
        ind_name = ind["name"]
        url = f"https://api.worldbank.org/v2/country/{country_path}/indicator/{ind_code}?format=json&per_page=1000&date={start_year}:{end_year}"

        source_id = str(uuid.uuid4())
        src_rec = SourceRecord(
            id=source_id,
            run_id=run_id,
            project_id=project_id,
            title=f"{ind_name} — World Bank",
            url=url,
            publisher="World Bank",
            source_type="api",
            tier=2,
            language="en",
            domain="data.worldbank.org"
        )
        sources.append(src_rec)

        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                observations = data[1] if isinstance(data, list) and len(data) > 1 else []
                
                rows = []
                for obs in observations or []:
                    val = obs.get("value")
                    if val is not None:
                        country_name = obs.get("country", {}).get("value") or obs.get("countryiso3code")
                        iso3 = obs.get("countryiso3code") or obs.get("country", {}).get("id")
                        year = obs.get("date")
                        unit = obs.get("unit") or ""
                        rows.append(f"{country_name} ({iso3}) {year}: {val} {unit}".strip())

                has_data = len(rows) > 0
                text_lines = [
                    f"World Bank indicator: {ind_name} [{ind_code}]",
                    f"Markets requested: {', '.join(iso_codes)}",
                    f"Period: {start_year}-{end_year}",
                    "",
                    "\n".join(rows) if has_data else "No data returned by the World Bank API for the requested markets/period."
                ]
                content_text = "\n".join(text_lines)

                contents.append(SourceContentRecord(
                    source_id=source_id,
                    run_id=run_id,
                    project_id=project_id,
                    content=content_text,
                    char_count=len(content_text),
                    content_type="api",
                    extract_ok=has_data,
                    extract_error=None if has_data else "no data returned"
                ))
            else:
                contents.append(SourceContentRecord(
                    source_id=source_id,
                    run_id=run_id,
                    project_id=project_id,
                    content=None,
                    char_count=0,
                    content_type="api",
                    extract_ok=False,
                    extract_error=f"HTTP {resp.status_code}"
                ))
        except Exception as e:
            contents.append(SourceContentRecord(
                source_id=source_id,
                run_id=run_id,
                project_id=project_id,
                content=None,
                char_count=0,
                content_type="api",
                extract_ok=False,
                extract_error=str(e)
            ))

    return sources, contents
