from pathlib import Path

from dotenv import load_dotenv
from google import genai

from schemas import ResearchPlan


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = genai.Client()


def create_research_plan(topic: str) -> ResearchPlan:

    prompt = f"""
You are an expert research planner.

Create a research plan for:

{topic}

Generate 5 to 8 focused research questions.

The questions should cover:

- Background
- Current state
- Important technologies
- Advantages
- Disadvantages
- Real-world applications
- Comparison
- Future direction

Make every question specific and researchable.
"""

    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=prompt
    )

    # For now, convert the response into our schema
    lines = interaction.output_text.splitlines()

    questions = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove numbering
        if "." in line[:3]:
            line = line.split(".", 1)[1].strip()

        if line:
            questions.append(line)

    return ResearchPlan(
        questions=questions
    )