"""
State definitions for LangGraph execution.
"""

from typing import TypedDict, List, Dict, Any, Optional
from schemas import (
    ResearchBrief,
    ResearchPlan,
    SourceRecord,
    SourceContentRecord,
    FindingRecord,
    ValidationVerdictRecord,
    AnalysisBundle,
    AnalysisNarrative
)


class ResearchState(TypedDict, total=False):
    # Run identifiers
    run_id: str
    project_id: str
    status: str

    # Brief & Planning
    brief: ResearchBrief
    raw_input: Dict[str, Any]
    plan: Optional[ResearchPlan]

    # Ingestion & Search
    queries: List[Dict[str, Any]]
    sources: List[SourceRecord]
    source_contents: List[SourceContentRecord]

    # Extraction
    findings: List[FindingRecord]

    # QC & Validations
    validations: List[ValidationVerdictRecord]

    # Analysis & Synthesis
    analysis: Optional[AnalysisBundle]
    analysis_narrative: Optional[AnalysisNarrative]

    # Final Report
    report_markdown: str
    report_metadata: Dict[str, Any]
    logs: List[str]
