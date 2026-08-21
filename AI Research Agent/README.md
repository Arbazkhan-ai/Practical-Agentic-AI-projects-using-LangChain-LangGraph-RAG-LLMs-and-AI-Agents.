# AI Research Agent 🔬

An autonomous research workflow built with **LangGraph**, **Google Gemini**, and **Pydantic**. The agent breaks down any research topic into focused investigative questions, performs deep grounded research with citations, and synthesizes the findings into a comprehensive Markdown research report.

---

## 🏗️ Architecture

```
[Topic Input] 
      │
      ▼
[Planner Node] ────► Decomposes topic into 5–8 focused, researchable questions
      │
      ▼
[Researcher Node] ──► Conducts grounded web search & empirical evidence gathering
      │
      ▼
[Report Writer] ────► Synthesizes findings into a structured Markdown brief with citations
      │
      ▼
[Final Report Output]
```

---

## 🚀 Getting Started

### 1. Prerequisites & Environment Setup
```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```ini
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

### 2. Running Research
```bash
# Run with default topic
python app/main.py

# Or pass a custom topic
python app/main.py "State of Agentic AI Frameworks in 2026"
```

---

## 📦 Project Structure
- `app/schemas.py` — Pydantic models for ResearchPlan, SourceItem, and ResearchFinding.
- `app/state.py` — TypedDict state definition for the LangGraph pipeline.
- `app/planner.py` — Generates decomposed research questions.
- `app/researcher.py` — Grounded search and factual evidence extraction.
- `app/report_writer.py` — Synthesizes evidence into a structured final report.
- `app/graph.py` — Assembles and compiles the StateGraph.
- `app/main.py` — CLI entrypoint and report visualizer.
