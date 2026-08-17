from langgraph.graph import StateGraph, START, END
from state import CodingState
from planner import plan_code_solution
from coder import generate_code_and_tests
from executor import execute_python_code_and_tests
from reviewer import review_code


def planner_node(state: CodingState) -> dict:
    """Creates initial architecture and implementation plan."""
    plan = plan_code_solution(
        task_description=state["task_description"],
        language=state.get("language", "python")
    )
    return {
        "plan": plan,
        "iteration_count": state.get("iteration_count", 0)
    }


def coder_node(state: CodingState) -> dict:
    """Generates code and unit tests based on the plan and any prior review feedback."""
    code, tests = generate_code_and_tests(
        task_description=state["task_description"],
        plan=state.get("plan"),
        previous_code=state.get("code", ""),
        review=state.get("review"),
        language=state.get("language", "python")
    )
    return {
        "code": code,
        "tests": tests,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def executor_node(state: CodingState) -> dict:
    """Executes the generated code and tests if language is python."""
    lang = state.get("language", "python").lower()
    if lang == "python":
        exec_result = execute_python_code_and_tests(
            code=state.get("code", ""),
            tests=state.get("tests", "")
        )
    else:
        exec_result = {
            "success": True,
            "stdout": f"Direct execution skipped for non-python language ({lang})",
            "stderr": "",
            "exit_code": 0
        }
    return {
        "execution_result": exec_result
    }


def reviewer_node(state: CodingState) -> dict:
    """Reviews code, tests, and execution results."""
    review = review_code(
        task_description=state["task_description"],
        code=state.get("code", ""),
        tests=state.get("tests", ""),
        plan=state.get("plan"),
        execution_result=state.get("execution_result"),
        language=state.get("language", "python")
    )
    return {
        "review": review,
        "is_completed": review.is_approved
    }


def should_continue(state: CodingState) -> str:
    """Determines whether to iterate or finish."""
    review = state.get("review")
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)

    if review and review.is_approved:
        return END
    
    if iteration_count >= max_iterations:
        return END

    return "coder"


# Graph Construction
builder = StateGraph(CodingState)

builder.add_node("planner", planner_node)
builder.add_node("coder", coder_node)
builder.add_node("executor", executor_node)
builder.add_node("reviewer", reviewer_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "coder")
builder.add_edge("coder", "executor")
builder.add_edge("executor", "reviewer")
builder.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "coder": "coder",
        END: END
    }
)

graph = builder.compile()
