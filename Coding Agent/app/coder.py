import re
from schemas import CodePlan, CodeReview
from llm_client import generate_llm_response
from typing import Optional, Tuple


def generate_code_and_tests(
    task_description: str,
    plan: Optional[CodePlan] = None,
    previous_code: str = "",
    review: Optional[CodeReview] = None,
    language: str = "python"
) -> Tuple[str, str]:
    """
    Generates or refines clean production-ready code and corresponding unit tests.
    """
    plan_info = ""
    if plan:
        steps = "\n".join([f"- {s}" for s in plan.architecture_steps])
        edge_cases = "\n".join([f"- {e}" for e in plan.edge_cases])
        plan_info = f"""
Implementation Plan:
Summary: {plan.task_summary}

Architecture Steps:
{steps}

Edge Cases to Handle:
{edge_cases}
"""

    feedback_info = ""
    if review and not review.is_approved:
        fixes = "\n".join([f"- {f}" for f in review.suggested_fixes])
        feedback_info = f"""
PREVIOUS CODE HAD ISSUES:
Review Feedback: {review.feedback}
Suggested Fixes:
{fixes}

Previous Code:
```{language}
{previous_code}
```
Please fix all identified issues.
"""

    prompt = f"""
You are an expert Senior Software Engineer.
Write clean, modular, robust, and fully working {language} code for the following task.

Task Description:
{task_description}
{plan_info}
{feedback_info}

Formatting Instructions:
Provide your response in two clearly labeled markdown blocks:
1. CODE BLOCK: The main implementation code.
2. TESTS BLOCK: Complete runnable unit tests covering core functionality and edge cases.

Example output format:
```{language}
# Main solution code
def solution():
    pass
```

```{language}-test
# Unit tests
import unittest

class TestSolution(unittest.TestCase):
    def test_example(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```
"""

    text = generate_llm_response(prompt)

    # Extract code blocks
    code_blocks = re.findall(r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)```", text, re.DOTALL)

    if len(code_blocks) >= 2:
        code = code_blocks[0].strip()
        tests = code_blocks[1].strip()
    elif len(code_blocks) == 1:
        code = code_blocks[0].strip()
        tests = "# No separate tests extracted\n"
    else:
        code = text.strip()
        tests = "# No separate tests extracted\n"

    return code, tests
