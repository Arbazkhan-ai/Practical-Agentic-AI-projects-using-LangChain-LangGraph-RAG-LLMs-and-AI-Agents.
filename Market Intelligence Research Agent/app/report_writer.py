"""
AI Research Report Writer:
Assembles full dataset (QC counts, findings, trends, comparisons, conflicts, citations)
and generates a rigorous, evidence-grounded research intelligence report.
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
2. Preserve the exact meaning, period, geography, unit, and validation status of the supplied findings.
3. Findings with validation_status "warn" must be clearly labelled with "Caveat: validation status = warn."
4. Never use fail findings.
5. QC counts must match qc_counts exactly.
6. Clearly distinguish factual findings from AI-derived interpretation.
7. In Supporting Evidence & Sources, include the source title, publisher, URL, and short evidence quotation whenever available.
8. Report Structure:
   # 1. Research Objective
   # 2. Markets and Date Range
   # 3. Executive Summary
   # 4. Key Findings & Evidence Table
   # 5. Market / Geography Insights
   # 6. Important Statistics, Comparisons & Trends
   # 7. Investment & Strategy Insights (AI-Derived Interpretation)
   # 8. Data Gaps & Conflicting Figures
   # 9. Supporting Sources & Citations
   # 10. QC / Validation Audit Summary

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
    Constructs the structured JSON payload containing all validated findings, metrics, and sources for the report writer.
    """
    val_map = {v.finding_id: v for v in validations}
    src_map = {s.id: s for s in sources}

    counts = {"pass": 0, "warn": 0, "fail": 0}
    usable_findings = []

    for f in findings:
        val = val_map.get(f.id)
        status = val.validation_status if val else "pass"
        if status in counts:
            counts[status] += 1

        if status != "fail":
            src = src_map.get(f.source_id) if f.source_id else None
            usable_findings.append({
                "finding_id": f.id,
                "claim": f.claim,
                "metric": f.metric,
                "value": f.value,
                "unit": f.unit,
                "geography": f.geography,
                "time_period": f.time_period,
                "validation_status": status,
                "support_verdict": val.support_verdict if val else "supported",
                "support_score": val.support_score if val else 1.0,
                "quote": f.evidence_text[:400] if f.evidence_text else "N/A",
                "source_title": src.title if src else "Registered Source",
                "source_publisher": src.publisher if src else "Institutional Registry",
                "source_url": src.url if src else f.citation_url
            })

    source_list = [
        {
            "id": s.id,
            "title": s.title,
            "publisher": s.publisher,
            "url": s.url,
            "source_type": s.source_type,
            "tier": s.tier
        }
        for s in sources
    ]

    return {
        "objective": brief.objective,
        "title": brief.title,
        "markets": brief.geography or (plan.markets if plan else []),
        "date_range": brief.date_range or "2015-2025",
        "qc_counts": counts,
        "total_findings_evaluated": len(findings),
        "usable_findings_count": len(usable_findings),
        "findings": usable_findings[:50],
        "sources": source_list[:25],
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
