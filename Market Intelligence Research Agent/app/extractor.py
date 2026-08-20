"""
AI Evidence Extractor:
Processes ingested text in balanced chunks and extracts strictly grounded factual findings,
metrics, numeric values, denominator definitions, and verbatim quotes.
"""

import uuid
from typing import List, Dict, Any, Optional
from schemas import ResearchPlan, SourceRecord, SourceContentRecord, FindingRecord
from llm_client import generate_llm_response, parse_json_safely


EXTRACTOR_SYSTEM_PROMPT = """You are a meticulous research evidence extractor for Eclectik, a Caribbean market-intelligence firm. From the SOURCE CONTENT provided, extract only concrete factual findings that are EXPLICITLY stated in that text.

Absolute rules:
- NEVER invent, infer, estimate, or generalize. If the text does not state it, do not output it.
- Every finding MUST include a verbatim quote copied word-for-word from the SOURCE CONTENT that directly supports the claim.
- Tag each extraction strictly as "sourced_fact". (Derived calculations are computed by Eclectik's deterministic engine separately).
- Preserves the exact denominator or measurement definition (e.g. "% of hotel food & beverage spend", "% of total merchandise imports", "commercial gross sales in JMD", "visitor spend per day in USD").
- Extract the exact location (page number, table number, cuadro, section) whenever discernible.
- If the text contains no qualifying findings, return an empty findings array.

Return ONLY a valid JSON object (no prose, no markdown) with exactly this shape:
{
  "findings": [
    {
      "claim": "one-sentence factual statement grounded strictly in the quote",
      "claim_type": "sourced_fact",
      "metric": "name of the measure or null",
      "value": 12.34,  // numeric value only or null
      "unit": "US$ / % / arrivals / JMD or null",
      "denominator_definition": "precise base/denominator or null",
      "market": "Country/market name or null",
      "period": "Exact observation year or range (e.g., 2023, 2018-2024) or null",
      "confidence": "high" | "medium" | "low",
      "quote": "verbatim excerpt copied from SOURCE CONTENT",
      "location_hint": "e.g. Page 52, Cuadro 4.3 or Section 2 or null"
    }
  ]
}
"""


def extract_findings_from_sources(
    plan: ResearchPlan,
    sources: List[SourceRecord],
    contents: List[SourceContentRecord],
    run_id: str,
    project_id: str,
    chunk_size: int = 10000,
    max_chunks_per_source: int = 3,
    max_total_chunks: int = 25
) -> List[FindingRecord]:
    """
    Chunks ingested content and runs AI Evidence Extractor on each chunk.
    """
    src_map = {s.id: s for s in sources}
    all_findings: List[FindingRecord] = []

    plan_context_lines = [
        f"Objective: {plan.research_objective}",
        f"Sub-questions: {'; '.join(plan.sub_questions[:4])}",
        f"Required metrics: {'; '.join(plan.required_metrics[:4])}",
        f"Markets: {', '.join(plan.markets[:6])}",
        f"Date range: {plan.date_range}"
    ]
    plan_block = "\n".join(plan_context_lines)

    chunks_processed = 0

    for content_rec in contents:
        if chunks_processed >= max_total_chunks:
            break
        if not content_rec.content or not content_rec.extract_ok:
            continue

        raw_text = content_rec.content
        src = src_map.get(content_rec.source_id)
        src_title = src.title if src else "Untitled"
        src_url = src.url if src else "N/A"
        src_pub = src.publisher if src else "Unknown"
        src_tier = src.tier if src else 5
        src_doc_type = src.document_type if src else "web_article"
        src_pub_date = src.publication_date if src else None

        # Split text into chunks
        text_chunks = [
            raw_text[i:i + chunk_size]
            for i in range(0, len(raw_text), chunk_size)
        ][:max_chunks_per_source]

        for idx, chunk in enumerate(text_chunks):
            if chunks_processed >= max_total_chunks:
                break
            chunks_processed += 1

            prompt = f"""RESEARCH PLAN CONTEXT (for relevance only - never copy values from here):
{plan_block}

SOURCE METADATA:
Title: {src_title}
Publisher: {src_pub} (Tier {src_tier})
Document Type: {src_doc_type}
URL: {src_url}
Chunk: {idx + 1} of {len(text_chunks)}

SOURCE CONTENT (extract findings ONLY from the text below):
{chunk}"""

            try:
                response = generate_llm_response(
                    prompt=prompt,
                    system_instruction=EXTRACTOR_SYSTEM_PROMPT,
                    json_mode=True,
                    temperature=0.0
                )
                data = parse_json_safely(response)
                items = data.get("findings", []) if isinstance(data, dict) else []

                for item in items:
                    claim = str(item.get("claim", "")).strip()
                    quote = str(item.get("quote", "")).strip()
                    if not claim or not quote:
                        continue

                    # Clean numeric value
                    val = item.get("value")
                    numeric_val = None
                    if val is not None:
                        try:
                            numeric_val = float(str(val).replace(",", "").strip())
                        except (ValueError, TypeError):
                            numeric_val = None

                    finding = FindingRecord(
                        id=str(uuid.uuid4()),
                        run_id=run_id,
                        project_id=project_id,
                        source_id=content_rec.source_id,
                        claim_type=item.get("claim_type", "sourced_fact"),
                        claim=claim,
                        metric=item.get("metric"),
                        value=numeric_val,
                        unit=item.get("unit"),
                        denominator_definition=item.get("denominator_definition"),
                        geography=item.get("market"),
                        time_period=item.get("period"),
                        confidence=item.get("confidence", "medium"),
                        evidence_text=quote,
                        page_section=item.get("location_hint") or content_rec.extracted_page,
                        citation_url=src_url,
                        source_tier=src_tier,
                        source_publisher=src_pub,
                        document_type=src_doc_type,
                        publication_date=src_pub_date
                    )
                    all_findings.append(finding)
            except Exception:
                continue

    return all_findings

