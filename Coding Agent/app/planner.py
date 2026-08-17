import json
from schemas import CodePlan
from llm_client import generate_llm_response


def plan_code_solution(task_description: str, language: str = "python") -> CodePlan:
    """
    Analyzes a coding task and creates a structured plan with architecture steps and edge cases.
    """
    prompt = f"""
You are an expert Software Architect and Lead Engineer.
Analyze the following programming task and create a detailed implementation plan.

Target Programming Language: {language}

Task Description:
{task_description}

Return a valid JSON object matching this schema:
{{
  "task_summary": "Summary of requirements and objectives",
  "language": "{language}",
  "architecture_steps": [
    "Step 1: Description",
    "Step 2: Description"
  ],
  "edge_cases": [
    "Edge case 1: Description",
    "Edge case 2: Description"
  ]
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
        return CodePlan(**data)
    except Exception:
        # Fallback parsing
        return CodePlan(
            task_summary=f"Implementation plan for: {task_description[:80]}...",
            language=language,
            architecture_steps=[
                "Define core data structures and interfaces",
                "Implement primary business logic and functions",
                "Add error handling and edge-case guards",
                "Write comprehensive unit tests"
            ],
            edge_cases=["Invalid inputs", "Boundary conditions", "Null / empty data"]
        )
