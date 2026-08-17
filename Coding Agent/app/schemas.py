from pydantic import BaseModel, Field
from typing import Optional, List


class CodePlan(BaseModel):
    task_summary: str = Field(
        description="High-level understanding and goal of the programming task"
    )
    language: str = Field(
        default="python",
        description="Target programming language for the solution"
    )
    architecture_steps: List[str] = Field(
        default_factory=list,
        description="Step-by-step implementation plan and architectural breakdown"
    )
    edge_cases: List[str] = Field(
        default_factory=list,
        description="Potential edge cases and failure modes to account for"
    )


class CodeReview(BaseModel):
    is_approved: bool = Field(
        description="True if the code meets all requirements, is bug-free, and well-structured"
    )
    feedback: str = Field(
        description="Detailed review comments, bug reports, or suggestions for improvement"
    )
    suggested_fixes: List[str] = Field(
        default_factory=list,
        description="Specific recommendations or patches needed if rejected"
    )
