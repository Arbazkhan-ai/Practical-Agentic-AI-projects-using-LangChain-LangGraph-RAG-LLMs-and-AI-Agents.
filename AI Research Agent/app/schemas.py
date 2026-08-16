from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    questions: list[str] = Field(
        description="A list of focused research questions"
    )