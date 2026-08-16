from pathlib import Path
from dotenv import load_dotenv
from google import genai


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

# Gemini client
client = genai.Client()


def research_question(question: str):

    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=f"""
You are a professional web researcher.

Research the following question:

{question}

Requirements:
- Search the web.
- Prefer official and authoritative sources.
- Use multiple sources when possible.
- Focus on current information.
- Do not invent facts.
- Summarize the evidence clearly.
""",
        tools=[
            {
                "type": "google_search"
            }
        ]
    )

    sources = []

    for step in interaction.steps:

        if step.type != "model_output":
            continue

        for content in step.content:

            if content.type != "text":
                continue

            if not content.annotations:
                continue

            for annotation in content.annotations:

                if annotation.type == "url_citation":

                    sources.append({
                        "title": annotation.title,
                        "url": annotation.url
                    })

    return {
        "question": question,
        "answer": interaction.output_text,
        "sources": sources
    }