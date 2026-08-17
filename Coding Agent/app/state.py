from typing import TypedDict, Optional, List, Dict, Any
from schemas import CodePlan, CodeReview


class CodingState(TypedDict):
    task_description: str
    language: str
    plan: Optional[CodePlan]
    code: str
    tests: str
    execution_result: Optional[Dict[str, Any]]
    review: Optional[CodeReview]
    iteration_count: int
    max_iterations: int
    is_completed: bool
