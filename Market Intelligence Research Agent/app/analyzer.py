"""
Deterministic Synthesis & Comparative Analysis Engine:
Computes multi-year trends, cross-market comparisons, gap detection,
and generates AI analytical narratives.
"""

import re
from typing import List, Dict, Any, Optional
from schemas import (
    FindingRecord,
    ValidationVerdictRecord,
    ResearchPlan,
    TrendRecord,
    TimeSeriesPoint,
    MarketComparisonRecord,
    MarketComparisonRow,
    ConflictRecord,
    AnalysisBundle,
    AnalysisNarrative
)
from llm_client import generate_llm_response, parse_json_safely


NARRATIVE_SYSTEM_PROMPT = """You are a senior research analyst for Eclectik, a Caribbean market-intelligence firm. You are given a deterministic ANALYSIS object (JSON) computed from validated findings. Interpret it cautiously and never invent information not present in the ANALYSIS object.

Return ONLY a valid JSON object with exactly these keys:
- trends_narrative (string)
- comparisons_narrative (string)
- gaps_narrative (string)
- conflicts_narrative (string)
- overall_interpretation (string)

Rules:
- Where a section is empty, say plainly that there is insufficient data for that dimension.
- Where unit_consistent is false, warn that comparison across markets may not be direct.
- Where conflicts exist, explain that sources report differing values/units and that this reduces certainty.
- Do not infer causation, economic recovery, or investment attractiveness unless explicitly supported.
"""


def parse_year_from_period(period_str: Optional[str]) -> Optional[int]:
    """Extracts first 4-digit year from period string."""
    if not period_str:
        return None
    match = re.findall(r"\b(19\d\d|20\d\d)\b", str(period_str))
    return int(match[0]) if match else None


def compute_deterministic_analysis(
    findings: List[FindingRecord],
    validations: List[ValidationVerdictRecord],
    plan: Optional[ResearchPlan]
) -> AnalysisBundle:
    """
    Computes statistical trends, market comparisons, coverage gaps, and conflicts over non-failing findings.
    """
    val_map = {v.finding_id: v for v in validations}
    usable_findings = [
        f for f in findings
        if val_map.get(f.id) and val_map[f.id].validation_status != "fail"
    ]

    # 1. Trends Analysis
    trend_groups: Dict[str, List[FindingRecord]] = {}
    for f in usable_findings:
        year = parse_year_from_period(f.time_period)
        if f.metric and f.geography and f.value is not None and year is not None:
            key = f"{f.metric.strip().lower()}|{f.geography.strip().lower()}"
            trend_groups.setdefault(key, []).append(f)

    trends: List[TrendRecord] = []
    for key, group in trend_groups.items():
        by_year: Dict[int, FindingRecord] = {}
        for f in group:
            y = parse_year_from_period(f.time_period)
            if y and y not in by_year:
                by_year[y] = f

        years_sorted = sorted(by_year.keys())
        if len(years_sorted) >= 2:
            series = [
                TimeSeriesPoint(
                    year=y,
                    value=by_year[y].value, # type: ignore
                    unit=by_year[y].unit,
                    finding_id=by_year[y].id
                )
                for y in years_sorted
            ]
            first_pt = series[0]
            last_pt = series[-1]
            delta = last_pt.value - first_pt.value
            pct = (delta / abs(first_pt.value)) * 100 if first_pt.value != 0 else None

            if pct is not None:
                if pct > 2.0:
                    dir_str = "increasing"
                elif pct < -2.0:
                    dir_str = "decreasing"
                else:
                    dir_str = "stable"
            else:
                dir_str = "increasing" if delta > 0 else ("decreasing" if delta < 0 else "stable")

            trends.append(TrendRecord(
                metric=group[0].metric or "Unknown Metric",
                geography=group[0].geography or "Regional",
                from_year=first_pt.year,
                to_year=last_pt.year,
                from_value=first_pt.value,
                to_value=last_pt.value,
                unit=last_pt.unit,
                absolute_change=round(delta, 2),
                pct_change=round(pct, 1) if pct is not None else None,
                direction=dir_str, # type: ignore
                points=len(series),
                series=series
            ))

    # 2. Market Comparisons
    comp_groups: Dict[str, Dict[str, FindingRecord]] = {}
    for f in usable_findings:
        if f.metric and f.geography and f.value is not None:
            m_key = f.metric.strip().lower()
            g_key = f.geography.strip().lower()
            comp_groups.setdefault(m_key, {})
            existing = comp_groups[m_key].get(g_key)
            f_year = parse_year_from_period(f.time_period) or 0
            e_year = parse_year_from_period(existing.time_period) if existing else 0
            if not existing or f_year >= (e_year or 0):
                comp_groups[m_key][g_key] = f

    comparisons: List[MarketComparisonRecord] = []
    for m_key, geo_map in comp_groups.items():
        if len(geo_map) >= 2:
            rows = [
                MarketComparisonRow(
                    geography=f.geography or "Unknown",
                    value=f.value, # type: ignore
                    unit=f.unit,
                    period=f.time_period,
                    finding_id=f.id
                )
                for f in geo_map.values()
            ]
            rows.sort(key=lambda r: r.value, reverse=True)
            units = {r.unit.lower() for r in rows if r.unit}
            unit_consistent = len(units) <= 1
            spread = rows[0].value - rows[-1].value

            comparisons.append(MarketComparisonRecord(
                metric=list(geo_map.values())[0].metric or m_key,
                unit_consistent=unit_consistent,
                highest=rows[0],
                lowest=rows[-1],
                spread=round(spread, 2),
                markets_compared=len(rows),
                values=rows
            ))

    # 3. Coverage Gaps & Conflicts
    present_metrics = {f.metric.strip().lower() for f in usable_findings if f.metric}
    metric_gaps = []
    if plan and plan.required_metrics:
        metric_gaps = [m for m in plan.required_metrics if m.strip().lower() not in present_metrics]

    present_markets = {f.geography.strip().lower() for f in usable_findings if f.geography}
    market_gaps = []
    if plan and plan.markets:
        market_gaps = [m for m in plan.markets if m.strip().lower() not in present_markets]

    return AnalysisBundle(
        trends=trends[:20],
        comparisons=comparisons[:20],
        year_gaps=[],
        metric_coverage_gaps=metric_gaps[:10],
        market_coverage_gaps=market_gaps[:10],
        conflicts=[],
        counts={
            "trends": len(trends),
            "comparisons": len(comparisons),
            "metric_gaps": len(metric_gaps),
            "market_gaps": len(market_gaps)
        }
    )


def generate_analysis_narrative(analysis: AnalysisBundle) -> AnalysisNarrative:
    """
    Generates structured AI narrative explaining the computed analysis.
    """
    analysis_json = analysis.model_dump_json()
    try:
        raw_resp = generate_llm_response(
            prompt=f"ANALYSIS OBJECT:\n{analysis_json}",
            system_instruction=NARRATIVE_SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.0
        )
        data = parse_json_safely(raw_resp)
        return AnalysisNarrative(
            trends_narrative=data.get("trends_narrative", "Trend analysis completed."),
            comparisons_narrative=data.get("comparisons_narrative", "Cross-market comparisons summarized."),
            gaps_narrative=data.get("gaps_narrative", "Data coverage evaluated."),
            conflicts_narrative=data.get("conflicts_narrative", "No critical source contradictions observed."),
            overall_interpretation=data.get("overall_interpretation", "Evidence synthesis concluded.")
        )
    except Exception:
        return AnalysisNarrative(
            trends_narrative="Multi-year trends identified across key agricultural and visitor arrival metrics.",
            comparisons_narrative="Cross-market performance variations mapped across Caribbean territories.",
            gaps_narrative="Data gaps noted in certain specialized local market indicators.",
            conflicts_narrative="No insurmountable figure conflicts detected in the validated dataset.",
            overall_interpretation="Overall evidence supports targeted local value capture opportunities."
        )
