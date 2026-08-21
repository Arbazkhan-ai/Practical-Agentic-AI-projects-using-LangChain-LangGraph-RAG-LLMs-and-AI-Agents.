from typing import TypedDict, List, Dict, Any, Optional
try:
    from app.schemas import ResearchPlan
except ImportError:
    from schemas import ResearchPlan


class ResearchState(TypedDict):
    topic: str
    research_plan: Optional[ResearchPlan]
    findings: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    final_report: str