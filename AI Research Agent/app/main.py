import sys

# Ensure UTF-8 console output encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from app.graph import graph
except ImportError:
    from graph import graph


def run_research(topic: str = "AI Agent frameworks in 2026"):
    print("=" * 75)
    print(f"🚀 [START] Launching AI Research Agent for Topic: '{topic}'")
    print("=" * 75)

    result = graph.invoke({
        "topic": topic,
        "research_plan": None,
        "findings": [],
        "sources": [],
        "final_report": ""
    })

    print("\n" + "=" * 75)
    print("📋 [PLAN] GENERATED RESEARCH PLAN")
    print("=" * 75)
    if result.get("research_plan"):
        for i, question in enumerate(result["research_plan"].questions, 1):
            print(f"  {i}. {question}")

    print("\n" + "=" * 75)
    print("🔍 [FINDINGS] INVESTIGATION RESULTS & GROUNDED CITATIONS")
    print("=" * 75)
    for i, finding in enumerate(result.get("findings", []), 1):
        print(f"\n[{i}] Question: {finding['question']}")
        print(f"Answer:\n{finding['answer']}")
        print("-" * 75)

    print("\n" + "=" * 75)
    print("📄 [REPORT] FINAL SYNTHESIZED RESEARCH REPORT")
    print("=" * 75)
    print(result.get("final_report", "No report generated."))
    print("\n" + "=" * 75)
    print("✅ [COMPLETE] Research pipeline finished successfully.")
    print("=" * 75)

    return result


if __name__ == "__main__":
    topic_input = sys.argv[1] if len(sys.argv) > 1 else "AI Agent frameworks in 2026"
    run_research(topic_input)