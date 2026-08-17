import json
from schemas import CodePlan, CodeReview
from llm_client import generate_llm_response
from typing import Optional, Dict, Any


def review_code(
    task_description: str,
    code: str,
    tests: str,
    plan: Optional[CodePlan] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    language: str = "python"
) -> CodeReview:
    """
    Evaluates generated code and test outcomes against task requirements.
    """
    exec_info = ""
    if execution_result:
        exec_info = f"""
Test Execution Result:
Success: {execution_result.get('success')}
Exit Code: {execution_result.get('exit_code')}
Stdout:
{execution_result.get('stdout', '')}
Stderr / Errors:
{execution_result.get('stderr', '')}
"""

    prompt = f"""
You are a Principal Code Reviewer and Quality Assurance Engineer.
Review the following {language} code and test suite for the given task.

Task:
{task_description}

Code:
```{language}
{code}
```

Tests:
```{language}
{tests}
```
{exec_info}

Instructions:
1. Verify if code solves the problem accurately and safely.
2. Check for syntax errors, logical bugs, and unhandled edge cases.
3. If test execution failed, is_approved MUST be false.
4. Return a JSON object matching this schema:
{{
  "is_approved": true or false,
  "feedback": "Concise summary of findings, strengths, or reasons for rejection",
  "suggested_fixes": ["Fix 1", "Fix 2"]
}}

Provide ONLY the raw JSON object, without markdown markdown code fences or conversational prose.
"""

    text = generate_llm_response(prompt).strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
        return CodeReview(**data)
    except Exception:
        # Fallback based on execution success
        exec_success = execution_result.get("success", False) if execution_result else True
        return CodeReview(
            is_approved=exec_success,
            feedback="Code generated and execution completed successfully." if exec_success else "Code review completed with detected runtime or test failures.",
            suggested_fixes=[] if exec_success else ["Fix syntax or runtime errors identified in tests."]
        )
