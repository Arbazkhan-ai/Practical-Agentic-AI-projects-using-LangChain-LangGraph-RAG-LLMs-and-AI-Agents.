import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = genai.Client()

FALLBACK_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    "gemini-2.5-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash-lite",
]


def generate_llm_response(prompt: str, preferred_model: str = None) -> str:
    """
    Generates text from Gemini with automatic fallback and retry on transient 503 / 429 errors.
    """
    candidate_models = []
    if preferred_model:
        candidate_models.append(preferred_model)
    for m in FALLBACK_MODELS:
        if m not in candidate_models:
            candidate_models.append(m)

    last_error = None
    for model_name in candidate_models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except (errors.ServerError, errors.ClientError) as err:
                last_error = err
                time.sleep(2 * (attempt + 1))
            except Exception as e:
                last_error = e
                break

    raise RuntimeError(f"All LLM candidate models failed. Last error: {last_error}")
