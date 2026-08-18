"""
LangGraph StateGraph workflow orchestration for the Market Intelligence Research Agent.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from state import ResearchState
from intake import validate_and_normalize_brief, initialize_research_run
from planner import generate_research_plan
from search import build_search_strategy, execute_search_and_scrape
from world_bank import fetch_world_bank_data
from extractor import extract_findings_from_sources
from qc import validate_findings
from analyzer import compute_deterministic_analysis, generate_analysis_narrative
from report_writer import generate_final_report


def intake_node(state: ResearchState) -> Dict[str, Any]:
    """Validates raw research brief and sets up run state."""
    raw_input = state.get("raw_input", {})
    init_state = initialize_research_run(raw_input)
    return {
        "run_id": init_state["run_id"],
        "project_id": init_state["project_id"],
        "status": "running",
        "brief": init_state["brief"],
        "logs": init_state["logs"] + ["Brief validated and normalized successfully."]
    }


def planner_node(state: ResearchState) -> Dict[str, Any]:
    """Generates the structured multi-angle, multilingual research plan."""
    brief = state["brief"]
    plan = generate_research_plan(brief)
    queries = build_search_strategy(plan, state["run_id"], state["project_id"])
    return {
        "plan": plan,
        "queries": queries,
        "logs": state.get("logs", []) + [
            f"Research plan created with {len(queries)} multilingual queries across {len(plan.search_languages)} languages."
        ]
    }


def search_and_ingest_node(state: ResearchState) -> Dict[str, Any]:
    """Executes web search & scraping as well as live World Bank API indicator queries."""
    run_id = state["run_id"]
    project_id = state["project_id"]
    plan = state["plan"]
    queries = state.get("queries", [])

    # 1. Web Search & Scrape
    web_sources, web_contents = execute_search_and_scrape(
        queries=queries,
        run_id=run_id,
        project_id=project_id,
        max_search_queries=8,
        max_scrape_targets=10
    )

    # 2. World Bank API Connector
    wb_sources, wb_contents = fetch_world_bank_data(
        plan=plan,
        run_id=run_id,
        project_id=project_id
    )

    all_sources = web_sources + wb_sources
    all_contents = web_contents + wb_contents

    return {
        "sources": all_sources,
        "source_contents": all_contents,
        "logs": state.get("logs", []) + [
            f"Ingested {len(all_sources)} sources ({len(web_sources)} web, {len(wb_sources)} World Bank indicator series)."
        ]
    }


def extractor_node(state: ResearchState) -> Dict[str, Any]:
    """Extracts factual findings, metrics, and verbatim evidence quotes."""
    plan = state["plan"]
    sources = state.get("sources", [])
    contents = state.get("source_contents", [])
    run_id = state["run_id"]
    project_id = state["project_id"]

    findings = extract_findings_from_sources(
        plan=plan,
        sources=sources,
        contents=contents,
        run_id=run_id,
        project_id=project_id,
        max_total_chunks=20
    )

    return {
        "findings": findings,
        "logs": state.get("logs", []) + [
            f"Extracted {len(findings)} factual findings with verbatim citations."
        ]
    }


def qc_node(state: ResearchState) -> Dict[str, Any]:
    """Performs deterministic referential checks and LLM claim-support verification."""
    findings = state.get("findings", [])
    sources = state.get("sources", [])
    run_id = state["run_id"]
    project_id = state["project_id"]

    validations = validate_findings(
        findings=findings,
        sources=sources,
        run_id=run_id,
        project_id=project_id,
        max_llm_qc=30
    )

    pass_count = sum(1 for v in validations if v.validation_status == "pass")
    warn_count = sum(1 for v in validations if v.validation_status == "warn")
    fail_count = sum(1 for v in validations if v.validation_status == "fail")

    return {
        "validations": validations,
        "logs": state.get("logs", []) + [
            f"QC completed: {pass_count} passed, {warn_count} warned, {fail_count} failed."
        ]
    }


def analyzer_node(state: ResearchState) -> Dict[str, Any]:
    """Computes trends, cross-market comparisons, coverage gaps, and AI narrative."""
    findings = state.get("findings", [])
    validations = state.get("validations", [])
    plan = state.get("plan")

    analysis = compute_deterministic_analysis(
        findings=findings,
        validations=validations,
        plan=plan
    )
    narrative = generate_analysis_narrative(analysis)

    return {
        "analysis": analysis,
        "analysis_narrative": narrative,
        "logs": state.get("logs", []) + [
            f"Computed {len(analysis.trends)} statistical trends and {len(analysis.comparisons)} cross-market comparisons."
        ]
    }


def report_writer_node(state: ResearchState) -> Dict[str, Any]:
    """Synthesizes the complete final research intelligence report in Markdown."""
    brief = state["brief"]
    plan = state.get("plan")
    findings = state.get("findings", [])
    validations = state.get("validations", [])
    sources = state.get("sources", [])
    analysis = state.get("analysis")
    narrative = state.get("analysis_narrative")

    report_md = generate_final_report(
        brief=brief,
        plan=plan,
        findings=findings,
        validations=validations,
        sources=sources,
        analysis=analysis,
        narrative=narrative
    )

    return {
        "status": "completed",
        "report_markdown": report_md,
        "report_metadata": {
            "title": brief.title,
            "run_id": state["run_id"],
            "project_id": state["project_id"],
            "total_sources": len(sources),
            "total_findings": len(findings)
        },
        "logs": state.get("logs", []) + ["Final Research Intelligence Report generated successfully."]
    }


# Assemble LangGraph StateGraph
builder = StateGraph(ResearchState)

builder.add_node("intake", intake_node)
builder.add_node("planner", planner_node)
builder.add_node("search_and_ingest", search_and_ingest_node)
builder.add_node("extractor", extractor_node)
builder.add_node("qc", qc_node)
builder.add_node("analyzer", analyzer_node)
builder.add_node("report_writer", report_writer_node)

builder.add_edge(START, "intake")
builder.add_edge("intake", "planner")
builder.add_edge("planner", "search_and_ingest")
builder.add_edge("search_and_ingest", "extractor")
builder.add_edge("extractor", "qc")
builder.add_edge("qc", "analyzer")
builder.add_edge("analyzer", "report_writer")
builder.add_edge("report_writer", END)

research_graph = builder.compile()
