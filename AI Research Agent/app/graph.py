from langgraph.graph import StateGraph, START, END

from state import ResearchState
from planner import create_research_plan


def planner_node(state: ResearchState):

    plan = create_research_plan(state["topic"])

    return {
        "research_plan": plan
    }


def researcher_node(state: ResearchState):

    plan = state["research_plan"]

    findings = []
    sources = []

    for question in plan.questions:

        # Temporary mock research
        finding = {
            "question": question,
            "answer": f"Research findings for: {question}"
        }

        findings.append(finding)

        sources.append({
            "question": question,
            "sources": []
        })

    return {
        "findings": findings,
        "sources": sources
    }


builder = StateGraph(ResearchState)

builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", END)

graph = builder.compile()