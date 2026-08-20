"""
AI Research Report Writer:
Assembles full dataset (QC counts, findings, trends, comparisons, conflicts, citations)
and generates a rigorous, evidence-grounded research intelligence report adhering to
three-tier attribution, comparability flagging, and 6-tier source quality standards.
"""

import json
from typing import List, Dict, Any, Optional
from schemas import (
    ResearchBrief,
    ResearchPlan,
    FindingRecord,
    ValidationVerdictRecord,
    SourceRecord,
    AnalysisBundle,
    AnalysisNarrative
)
from llm_client import generate_llm_response


REPORT_WRITER_SYSTEM_PROMPT = """You are a senior research report writer for Eclectik, a Caribbean market-intelligence firm. Turn the supplied DATASET into a clear, professional, evidence-grounded research report.

Rules:
1. Use ONLY the information in the DATASET. Never invent numbers, statistics, sources, markets, geographies, years, values, claims, or conclusions.
2. Strictly enforce THREE-TIER ATTRIBUTION throughout the report:
   - Tag direct empirical data as **[Sourced Fact]** with verbatim quote and specific page/table citation.
   - Tag computed multi-year growth rates, percentage changes, spreads, and multiplier estimates as **[Eclectik-Derived Calculation]**.
   - Tag strategic analysis, implications, and recommendations as **[AI-Derived Interpretation]**.
3. In Section 6 (Comparative Benchmark Table), include columns for:
   - Market
   - Value & Unit
   - Time Period
   - Denominator / Methodology Definition
   - Comparability Status (e.g. Directly Comparable, Methodology Divergent) with caveat notes.
4. In Section 9 (Source & Citation Register), list sources with their 6-Tier Quality Rank (Tier 1 Multilateral to Tier 6 Social), Document Type, Publication Date, and Page/Section citation.
5. In Section 10 (QC & Validation Audit), summarize both Grounding Verification (substring/semantic match) and Source Metadata Validity (document type, publication date, and page count checks).
6. Report Structure:
   # 1. Research Objective & Context
   # 2. Scope, Geographic Coverage & Temporal Window
   # 3. Executive Summary
   # 4. Key Empirical Findings (Strictly [Sourced Fact] with Verbatim Grounding)
   # 5. Market & Supply Chain Analysis
   # 6. Quantitative Indicators, Cross-Market Benchmarks & Comparability Analysis
   # 7. Multi-Year Trends & Multipliers [Eclectik-Derived Calculations]
   # 8. Strategic Recommendations & Investment Insights [AI-Derived Interpretation]
   # 9. Supporting Source Register & Citation Index (6-Tier Quality Standard)
   # 10. QC & Data Integrity Audit Summary

Return ONLY the complete report in clean GitHub-Flavored Markdown. No preamble, no conversational filler."""


def assemble_report_dataset(
    brief: ResearchBrief,
    plan: Optional[ResearchPlan],
    findings: List[FindingRecord],
    validations: List[ValidationVerdictRecord],
    sources: List[SourceRecord],
    analysis: Optional[AnalysisBundle],
    narrative: Optional[AnalysisNarrative]
) -> Dict[str, Any]:
    """
    Constructs the structured JSON payload containing all validated findings, metrics, metadata,
    and comparability flags for the report writer.
    """
    val_map = {v.finding_id: v for v in validations}
    src_map = {s.id: s for s in sources}

    counts = {"pass": 0, "warn": 0, "fail": 0}
    metadata_counts = {"pass": 0, "warn": 0, "fail": 0}
    usable_findings = []

    for f in findings:
        val = val_map.get(f.id)
        status = val.validation_status if val else "pass"
        meta_st = val.metadata_status if val else "pass"
        
        if status in counts:
            counts[status] += 1
        if meta_st in metadata_counts:
            metadata_counts[meta_st] += 1

        if status != "fail":
            src = src_map.get(f.source_id) if f.source_id else None
            usable_findings.append({
                "finding_id": f.id,
                "claim_type": f.claim_type,
                "claim": f.claim,
                "metric": f.metric,
                "value": f.value,
                "unit": f.unit,
                "denominator_definition": f.denominator_definition or "Unspecified",
                "geography": f.geography,
                "time_period": f.time_period,
                "validation_status": status,
                "support_verdict": val.support_verdict if val else "supported",
                "support_score": val.support_score if val else 1.0,
                "quote": f.evidence_text[:400] if f.evidence_text else "N/A",
                "page_section": f.page_section or "N/A",
                "source_title": src.title if src else "Registered Source",
                "source_publisher": src.publisher if src else "Institutional Registry",
                "source_tier": src.tier if src else f.source_tier or 5,
                "document_type": src.document_type if src else f.document_type or "web_article",
                "publication_date": src.publication_date if src else f.publication_date or "date_unspecified",
                "source_url": src.url if src else f.citation_url
            })

    source_list = [
        {
            "id": s.id,
            "title": s.title,
            "publisher": s.publisher,
            "url": s.url,
            "tier": s.tier,
            "institution_category": s.institution_category,
            "document_type": s.document_type,
            "content_format": s.content_format,
            "publication_date": s.publication_date or "date_unspecified",
            "page_count": s.page_count
        }
        for s in sources
    ]

    return {
        "objective": brief.objective,
        "title": brief.title,
        "markets": brief.geography or (plan.markets if plan else []),
        "date_range": brief.date_range or "2015-2025",
        "qc_counts": counts,
        "qc_metadata_counts": metadata_counts,
        "total_findings_evaluated": len(findings),
        "usable_findings_count": len(usable_findings),
        "findings": usable_findings[:50],
        "sources": source_list[:30],
        "analysis": analysis.model_dump() if analysis else None,
        "analysis_narrative": narrative.model_dump() if narrative else None
    }


def generate_final_report(
    brief: ResearchBrief,
    plan: Optional[ResearchPlan],
    findings: List[FindingRecord],
    validations: List[ValidationVerdictRecord],
    sources: List[SourceRecord],
    analysis: Optional[AnalysisBundle],
    narrative: Optional[AnalysisNarrative]
) -> str:
    """
    Invokes the AI Report Writer to produce the final comprehensive Markdown report.
    """
    dataset = assemble_report_dataset(
        brief=brief,
        plan=plan,
        findings=findings,
        validations=validations,
        sources=sources,
        analysis=analysis,
        narrative=narrative
    )

    prompt = f"""Write the complete market intelligence research report from the DATASET below.

DATASET (JSON):
{json.dumps(dataset, indent=2)}"""

    report_md = generate_llm_response(
        prompt=prompt,
        system_instruction=REPORT_WRITER_SYSTEM_PROMPT,
        json_mode=False,
        temperature=0.0
    )

    return report_md.strip()

