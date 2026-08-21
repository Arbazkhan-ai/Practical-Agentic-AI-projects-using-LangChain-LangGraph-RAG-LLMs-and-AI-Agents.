from pydantic import BaseModel, Field
from typing import List, Optional


class ResearchPlan(BaseModel):
    topic: Optional[str] = Field(default=None, description="Topic of research")
    questions: List[str] = Field(
        default_factory=list,
        description="A list of focused research questions"
    )


class SourceItem(BaseModel):
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source")


class ResearchFinding(BaseModel):
    question: str = Field(description="Question investigated")
    answer: str = Field(description="Detailed factual answer with citations")
    sources: List[SourceItem] = Field(default_factory=list, description="Authoritative citations")