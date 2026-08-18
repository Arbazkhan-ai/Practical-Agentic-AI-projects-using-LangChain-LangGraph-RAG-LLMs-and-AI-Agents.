"""
Intake, brief validation, normalization, and project state initialization.
"""

import uuid
import re
from typing import Dict, Any, List
from schemas import ResearchBrief
from config import DEFAULT_CARIBBEAN_MARKETS


def parse_string_to_list(val: Any) -> List[str]:
    """Helper to split string by newlines, commas, or semicolons."""
    if not val:
        return []
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    
    parts = re.split(r"[\n,;]+", str(val))
    return [p.strip() for p in parts if p.strip()]


def validate_and_normalize_brief(input_data: Dict[str, Any]) -> ResearchBrief:
    """
    Validates required fields from intake brief and normalizes geography / questions.
    """
    title = str(input_data.get("title", "")).strip()
    if not title:
        raise ValueError("Missing required field: Research Title / Topic")

    objective = str(input_data.get("objective", "")).strip()
    if not objective:
        raise ValueError("Missing required field: Research Objective")

    raw_questions = input_data.get("questions")
    questions = parse_string_to_list(raw_questions)
    if not questions:
        raise ValueError("Missing required field: Specific Research Questions")

    raw_geo = input_data.get("geography")
    geo_list = parse_string_to_list(raw_geo)
    used_caribbean_default = len(geo_list) == 0

    date_range = str(input_data.get("date_range", "2015-2025")).strip() or "2015-2025"
    report_lang = str(input_data.get("report_language", "English")).strip() or "English"
    instructions = str(input_data.get("instructions", "")).strip() or None
    priority_themes = str(input_data.get("priority_themes", "")).strip() or None

    return ResearchBrief(
        title=title,
        objective=objective,
        questions=questions,
        geography=geo_list if not used_caribbean_default else [m["market"] for m in DEFAULT_CARIBBEAN_MARKETS],
        used_caribbean_default=used_caribbean_default,
        date_range=date_range,
        report_language=report_lang,
        priority_themes=priority_themes,
        instructions=instructions
    )


def initialize_research_run(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initializes a new research run and project session with unique UUIDs.
    """
    brief = validate_and_normalize_brief(raw_input)
    project_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    return {
        "run_id": run_id,
        "project_id": project_id,
        "status": "queued",
        "brief": brief,
        "raw_input": raw_input,
        "logs": [f"Run {run_id} initialized for project '{brief.title}'"]
    }
