from graph import graph


result = graph.invoke({
    "topic": "AI Agent frameworks in 2026",
    "research_plan": None,
    "findings": [],
    "sources": [],
    "final_report": ""
})


print("\n===== RESEARCH PLAN =====\n")

for i, question in enumerate(
    result["research_plan"].questions,
    1
):
    print(f"{i}. {question}")


print("\n===== FINDINGS =====\n")

for finding in result["findings"]:

    print("Question:")
    print(finding["question"])

    print("\nAnswer:")
    print(finding["answer"])

    print("-" * 60)