from langgraph.graph import StateGraph, START, END

try:
    from app.state import ResearchState
    from app.planner import create_research_plan
    from app.researcher import research_question
    from app.report_writer import write_research_report
except ImportError:
    from state import ResearchState
    from planner import create_research_plan
    from researcher import research_question
    from report_writer import write_research_report


def planner_node(state: ResearchState) -> dict:
    """Generates the structured research plan and key questions."""
    plan = create_research_plan(state["topic"])
    return {
        "research_plan": plan
    }


def researcher_node(state: ResearchState) -> dict:
    """Researches each question in the plan and gathers grounded citations."""
    plan = state.get("research_plan")
    if not plan or not plan.questions:
        return {
            "findings": [],
            "sources": []
        }

    findings = []
    sources = []

    for question in plan.questions:
        res = research_question(question)
        findings.append({
            "question": question,
            "answer": res.get("answer", "")
        })
        sources.append({
            "question": question,
            "sources": res.get("sources", [])
        })

    return {
        "findings": findings,
        "sources": sources
    }


def report_writer_node(state: ResearchState) -> dict:
    """Synthesizes all findings into a complete Markdown research report."""
    report = write_research_report(
        topic=state["topic"],
        findings=state.get("findings", []),
        sources=state.get("sources", [])
    )
    return {
        "final_report": report
    }


builder = StateGraph(ResearchState)

builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)
builder.add_node("writer", report_writer_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", END)

graph = builder.compile()