import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from graph import graph


def run_coding_agent(task_prompt: str, language: str = "python", max_iterations: int = 3):
    print("=" * 70)
    print(f"[START] Coding Agent Task: {task_prompt}")
    print(f"Language: {language} | Max Iterations: {max_iterations}")
    print("=" * 70)

    initial_state = {
        "task_description": task_prompt,
        "language": language,
        "plan": None,
        "code": "",
        "tests": "",
        "execution_result": None,
        "review": None,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "is_completed": False
    }

    result = graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("=== [PLAN] ARCHITECTURE PLAN ===")
    print("=" * 70)
    plan = result.get("plan")
    if plan:
        print(f"Summary: {plan.task_summary}")
        print("\nSteps:")
        for i, step in enumerate(plan.architecture_steps, 1):
            print(f"  {i}. {step}")
        print("\nEdge Cases Considered:")
        for edge in plan.edge_cases:
            print(f"  - {edge}")

    print("\n" + "=" * 70)
    print("=== [CODE] FINAL GENERATED CODE ===")
    print("=" * 70)
    print(result.get("code", ""))

    print("\n" + "=" * 70)
    print("=== [TESTS] GENERATED UNIT TESTS ===")
    print("=" * 70)
    print(result.get("tests", ""))

    exec_res = result.get("execution_result")
    if exec_res:
        print("\n" + "=" * 70)
        print("=== [EXECUTION] TEST RUN STATUS ===")
        print("=" * 70)
        print(f"Success: {exec_res.get('success')}")
        print(f"Stdout:\n{exec_res.get('stdout', '').strip()}")
        if exec_res.get("stderr"):
            print(f"Stderr:\n{exec_res.get('stderr', '').strip()}")

    review = result.get("review")
    if review:
        print("\n" + "=" * 70)
        print("=== [REVIEW] CODE REVIEW SUMMARY ===")
        print("=" * 70)
        print(f"Approved: {review.is_approved}")
        print(f"Feedback: {review.feedback}")
        print(f"Total Iterations: {result.get('iteration_count')}")

    return result


if __name__ == "__main__":
    sample_task = (
        "Write a ThreadSafeLRUCache class in Python with get(key), put(key, value), "
        "and get_stats() methods with TTL (time to live in seconds) support per entry."
    )
    run_coding_agent(sample_task)
