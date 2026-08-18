"""
Search Engine & Web Content Ingestion:
Executes queries via Firecrawl API or DuckDuckGo fallback, matches domain registry,
and extracts clean markdown/text from target web pages and PDFs.
"""

import os
import re
import uuid
import urllib.parse
from typing import List, Dict, Any, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from schemas import ResearchPlan, SourceRecord, SourceContentRecord
from config import SOURCE_REGISTRY

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


def extract_host(url: str) -> Optional[str]:
    """Extracts cleaned hostname from URL."""
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        return re.sub(r"^www\.", "", netloc)
    except Exception:
        return None


def match_registry_domain(host: str) -> Tuple[Optional[str], int, str]:
    """
    Matches host against SOURCE_REGISTRY to determine publisher name, tier, and region type.
    """
    if not host:
        return None, 5, "web"

    best_match = None
    for r in SOURCE_REGISTRY:
        d = r["domain"].lower()
        if host == d or host.endswith("." + d):
            if not best_match or r.get("tier", 5) < best_match.get("tier", 5):
                best_match = r

    if best_match:
        region = best_match.get("region", "web")
        if region == "regional":
            source_type = "regional"
        elif region == "international":
            source_type = "intl"
        elif region in ("french_caribbean", "national"):
            source_type = "gov"
        else:
            source_type = "web"
        return best_match.get("name"), best_match.get("tier", 1), source_type

    return host, 5, "web"


def build_search_strategy(plan: ResearchPlan, run_id: str, project_id: str) -> List[Dict[str, Any]]:
    """
    Flattens multilingual search queries into structured query items.
    """
    queries = []
    sq = plan.search_queries or {}
    for lang, q_list in sq.items():
        for q in q_list:
            if not q or not str(q).strip():
                continue
            queries.append({
                "run_id": run_id,
                "project_id": project_id,
                "query_text": str(q).strip(),
                "language": lang,
                "source_type": plan.preferred_source_types[0] if plan.preferred_source_types else "web"
            })
    return queries


def search_web_query(query_text: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Executes a single web search query using Firecrawl if configured, or DuckDuckGo search fallback.
    """
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    results = []

    if firecrawl_key and firecrawl_key != "your_firecrawl_api_key_here":
        try:
            resp = requests.post(
                "https://api.firecrawl.dev/v2/search",
                headers={"Authorization": f"Bearer {firecrawl_key}"},
                json={"query": query_text, "limit": limit, "sources": ["web"]},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                web_items = data.get("data", {}).get("web", []) or data.get("data", {}).get("results", [])
                for item in web_items:
                    results.append({
                        "url": item.get("url") or item.get("link"),
                        "title": item.get("title") or item.get("metadata", {}).get("title"),
                        "description": item.get("description") or item.get("snippet")
                    })
                return results
        except Exception:
            pass

    # DuckDuckGo fallback
    if HAS_DDGS:
        try:
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query_text, max_results=limit))
                for r in ddg_results:
                    results.append({
                        "url": r.get("href"),
                        "title": r.get("title"),
                        "description": r.get("body")
                    })
                return results
        except Exception:
            pass

    return results


def scrape_url_content(url: str, timeout: int = 15) -> Tuple[bool, str, str]:
    """
    Fetches and extracts clean markdown/text from a target URL.
    Returns (success, content, error_msg).
    """
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if firecrawl_key and firecrawl_key != "your_firecrawl_api_key_here":
        try:
            resp = requests.post(
                "https://api.firecrawl.dev/v2/scrape",
                headers={"Authorization": f"Bearer {firecrawl_key}"},
                json={"url": url, "formats": ["markdown"], "onlyMainContent": False, "timeout": 30000},
                timeout=35
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                md = data.get("markdown", "")
                if md and len(md.strip()) > 50:
                    return True, md.strip(), ""
        except Exception:
            pass

    # Direct requests + BeautifulSoup fallback
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            # Remove scripts and styles
            for elem in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                elem.decompose()
            text = soup.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return True, text[:25000], ""
            return False, "", "Extracted content too short"
        return False, "", f"HTTP status {r.status_code}"
    except Exception as e:
        return False, "", str(e)


def execute_search_and_scrape(
    queries: List[Dict[str, Any]],
    run_id: str,
    project_id: str,
    max_search_queries: int = 10,
    max_scrape_targets: int = 15
) -> Tuple[List[SourceRecord], List[SourceContentRecord]]:
    """
    Executes search over prioritized queries, deduplicates domains, and scrapes top target sources.
    """
    seen_urls = set()
    sources: List[SourceRecord] = []

    # Run top queries
    for q in queries[:max_search_queries]:
        results = search_web_query(q["query_text"], limit=6)
        for r in results:
            url = r.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            host = extract_host(url)
            publisher, tier, source_type = match_registry_domain(host)

            src_rec = SourceRecord(
                id=str(uuid.uuid4()),
                run_id=run_id,
                project_id=project_id,
                title=r.get("title") or host or "Untitled Document",
                url=url,
                publisher=publisher,
                source_type=source_type,
                tier=tier,
                language=q.get("language", "en"),
                domain=host
            )
            sources.append(src_rec)

    # Sort sources: Tier 1 authoritative first, PDFs prioritized
    def sort_key(s: SourceRecord):
        is_pdf = 0 if ".pdf" in s.url.lower() else 1
        return (s.tier, is_pdf)

    sources.sort(key=sort_key)
    targets = sources[:max_scrape_targets]

    contents: List[SourceContentRecord] = []
    for src in targets:
        ok, text, err = scrape_url_content(src.url)
        content_type = "pdf" if ".pdf" in src.url.lower() else "html"
        contents.append(SourceContentRecord(
            source_id=src.id,
            run_id=run_id,
            project_id=project_id,
            content=text if ok else None,
            char_count=len(text) if text else 0,
            content_type=content_type,
            extract_ok=ok,
            extract_error=err if not ok else None
        ))

    return sources, contents
