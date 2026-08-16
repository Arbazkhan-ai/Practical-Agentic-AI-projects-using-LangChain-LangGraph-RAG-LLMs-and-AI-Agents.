from typing import TypedDict
from schemas import ResearchPlan


class ResearchState(TypedDict):

    topic: str

    research_plan: ResearchPlan

    findings: list[dict]

    sources: list[dict]

    final_report: str