import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors

try:
    from app.schemas import ResearchPlan
except ImportError:
    from schemas import ResearchPlan


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

FALLBACK_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash-lite",
]


def create_research_plan(topic: str) -> ResearchPlan:
    """Generates a structured research plan with 5-8 focused investigation questions."""
    prompt = f"""
You are an expert research planner.

Create a comprehensive research plan for the following topic:
{topic}

Generate 5 to 8 focused research questions covering:
- Background & Core Concepts
- Current Architecture & Important Technologies
- Key Advantages & Benefits
- Limitations & Challenges
- Real-World Use Cases & Production Deployments
- Comparison with Alternatives
- Future Directions & Trends

Return the questions as a numbered list (e.g., 1. ..., 2. ...).
"""
    if client:
        for model_name in FALLBACK_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    lines = response.text.splitlines()
                    questions = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        # Remove markdown list markers or numbers
                        cleaned = re.sub(r"^(\d+[\.\)]|\*|-)\s*", "", line).strip()
                        if cleaned and len(cleaned) > 10 and "?" in cleaned:
                            questions.append(cleaned)
                        elif cleaned and len(cleaned) > 15 and not line.startswith("#"):
                            questions.append(cleaned)
                    
                    if len(questions) >= 3:
                        return ResearchPlan(topic=topic, questions=questions[:8])
            except Exception:
                continue

    # Fallback default structured plan
    fallback_questions = [
        f"What are the foundational architectures and key design principles of {topic}?",
        f"What are the leading frameworks, libraries, and runtime environments powering {topic}?",
        f"What are the primary operational advantages and efficiency gains offered by {topic}?",
        f"What are the critical limitations, latency bottlenecks, and security challenges in {topic}?",
        f"What are high-impact real-world production use cases demonstrating success with {topic}?",
        f"How does {topic} compare against legacy or alternative paradigms?",
        f"What emerging trends and roadmap developments are shaping the future of {topic} over the next 3-5 years?"
    ]
    return ResearchPlan(topic=topic, questions=fallback_questions)