"""
AI Research Planner: Generates strict multi-angle, multilingual research plans with institutional search queries.
"""

from typing import Dict, Any, List
from schemas import ResearchBrief, ResearchPlan
from config import DEFAULT_CARIBBEAN_MARKETS, SOURCE_REGISTRY
from llm_client import generate_llm_response, parse_json_safely


PLANNER_SYSTEM_PROMPT = """You are a senior research planner for Eclectik, a Caribbean market-intelligence firm. Transform a structured research brief into a strict research PLAN only. You do NOT perform research and you do NOT invent facts, statistics, or findings. You only design the research strategy. 

Return ONLY a valid JSON object (no prose, no markdown) with EXACTLY these keys:
- research_objective (string)
- key_research_angles (array of strings)
- sub_questions (array of strings)
- markets (array of strings)
- date_range (string)
- required_metrics (array of strings)
- key_concepts (array of strings)
- search_queries (object with keys en, fr, es, nl, each an array of strings)
- preferred_source_types (array of strings)
- priority_domains (array of strings)
- required_evidence (array of strings)
- expected_comparisons (array of strings)
- search_languages (array of language codes)

Rules:
1. If markets are not provided in the brief, use the supplied Caribbean coverage list.
2. Choose search_languages based on the markets (e.g. French for Guadeloupe/Martinique/Haiti, Spanish for Cuba/Dominican Republic/Puerto Rico, Dutch for Aruba/Curacao/Suriname, English broadly).
3. Ensure key_research_angles, sub_questions, required_metrics, and search_queries deeply cover:
   - tourism sector size & visitor demand
   - local food & agriculture production
   - food imports & import dependency
   - hotel & restaurant purchasing and tourism-agriculture supply chains
   - local value capture & named farm-to-table initiatives
   - barriers (logistics, certification, pricing, seasonality, financing)
   - concrete investment opportunities.

MULTILINGUAL QUERY DECOMPOSITION (mandatory):
Produce 15-25 search_queries TOTAL, distributed across every relevant language.
Within each language generate BOTH:
(a) broad topic queries with NO domain filter, AND
(b) institution-targeted queries appending site: filters like (site:fao.org OR site:iica.int).

Choose site: domains from this authoritative registry:
- English & Regional: caricom.org, oecs.int, caribank.org, eccb-centralbank.org, onecaribbean.org, fao.org, iica.int, worldbank.org, cepal.org, iadb.org, imf.org, untourism.int
- French: insee.fr, iedom.fr, data.gouv.fr, ec.europa.eu, fao.org, iica.int, cepal.org
- Spanish: cepal.org, fao.org, iica.int, iadb.org, one.gob.do, onei.gob.cu
- Dutch: cbs.nl, centralbank.cw, cbaruba.org, fao.org, cepal.org
"""


def generate_research_plan(brief: ResearchBrief) -> ResearchPlan:
    """
    Invokes the AI Research Planner to produce a strict JSON ResearchPlan.
    """
    coverage_summary = "; ".join([
        f"{m['market']} [{','.join(m['languages'])}]" for m in DEFAULT_CARIBBEAN_MARKETS
    ])
    
    user_prompt = f"""RESEARCH BRIEF
Title: {brief.title}
Objective: {brief.objective}
Research questions:
{chr(10).join(f"- {q}" for q in brief.questions)}
Geography provided by user: {brief.geography}
Use Caribbean default coverage: {brief.used_caribbean_default}
Date range: {brief.date_range}
Final report language: {brief.report_language}
Priority themes: {brief.priority_themes or "N/A"}
Additional instructions: {brief.instructions or "N/A"}

CARIBBEAN COVERAGE LIST (use when geography not specified):
{coverage_summary}

AUTHORITATIVE DOMAINS:
{', '.join([r['domain'] for r in SOURCE_REGISTRY])}

Return the strict JSON research plan now."""

    raw_response = generate_llm_response(
        prompt=user_prompt,
        system_instruction=PLANNER_SYSTEM_PROMPT,
        json_mode=True,
        temperature=0.2
    )

    data = parse_json_safely(raw_response)
    if not data:
        # Fallback plan generation if parsing encountered unexpected format
        data = {
            "research_objective": brief.objective,
            "key_research_angles": ["Tourism Demand", "Local Agricultural Supply", "Supply Chain Value Capture"],
            "sub_questions": brief.questions,
            "markets": brief.geography or [m["market"] for m in DEFAULT_CARIBBEAN_MARKETS[:5]],
            "date_range": brief.date_range or "2015-2025",
            "required_metrics": ["Tourist arrivals", "Food import bill", "Agriculture % of GDP"],
            "key_concepts": ["Farm-to-table", "Agritourism", "Import substitution"],
            "search_queries": {
                "en": [f"{brief.title} Caribbean statistics site:onecaribbean.org", f"{brief.title} market size"],
                "fr": [f"{brief.title} Caraïbes statistiques site:insee.fr"],
                "es": [f"{brief.title} Caribe estadísticas site:cepal.org"],
                "nl": [f"{brief.title} Cariben statistieken site:cbs.nl"]
            },
            "preferred_source_types": ["web", "api", "pdf"],
            "priority_domains": ["caricom.org", "onecaribbean.org", "worldbank.org", "fao.org"],
            "required_evidence": ["Quantitative metrics", "Verbatim institutional citations"],
            "expected_comparisons": ["Import share by country", "Visitor spending on local produce"],
            "search_languages": ["en", "fr", "es", "nl"]
        }

    return ResearchPlan(
        research_objective=data.get("research_objective", brief.objective),
        key_research_angles=data.get("key_research_angles", []),
        sub_questions=data.get("sub_questions", brief.questions),
        markets=data.get("markets", brief.geography or []),
        date_range=data.get("date_range", brief.date_range or "2015-2025"),
        required_metrics=data.get("required_metrics", []),
        key_concepts=data.get("key_concepts", []),
        search_queries=data.get("search_queries", {}),
        preferred_source_types=data.get("preferred_source_types", ["web", "api"]),
        priority_domains=data.get("priority_domains", []),
        required_evidence=data.get("required_evidence", []),
        expected_comparisons=data.get("expected_comparisons", []),
        search_languages=data.get("search_languages", ["en", "fr", "es", "nl"])
    )
