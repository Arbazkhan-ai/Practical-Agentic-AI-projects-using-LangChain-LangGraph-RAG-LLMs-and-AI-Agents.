# Practical Agentic AI Projects 🤖⚡

A comprehensive, production-grade collection of **Agentic AI**, **LangGraph**, **LangChain**, **RAG**, **Local LLMs**, and **Multi-Agent Systems** built with Python and modern web technologies.

---

## 🌟 Projects Overview

| # | Project | Technology Stack | Key Capabilities |
|---|---|---|---|
| **1** | [**Market Intelligence Research Agent**](./Market%20Intelligence%20Research%20Agent/) | LangGraph, Gemini 2.5/3.5, Supabase, ReportLab, n8n | 6-Tier source quality hierarchy, 3-tier fact attribution, cross-market comparability, automated 21-section PDF generation, and n8n workflow integration. |
| **2** | [**Coding Agent**](./Coding%20Agent/) | LangGraph, Google Gemini, Python Subprocess Sandbox | Autonomous Plan-Code-Test-Review loop. Generates modular code, writes comprehensive unit tests, executes tests in an isolated sandbox, and iterates based on review feedback. |
| **3** | [**AI Research Agent**](./AI%20Research%20Agent/) | LangGraph, Gemini Search Grounding, Pydantic | Decomposes complex topics into structured questions, gathers grounded evidence and web citations, and compiles an executive research brief. |
| **4** | [**English Speaking Practice (TalkWithLeo)**](./English%20Speaking%20Practice/) | Local Ollama (`gemma3:4b`), Web Speech API, Vanilla JS | Hands-free continuous conversational buddy ("Leo") with animated SVG avatar, real-time speech synthesis, and post-session fluency analysis. |
| **5** | [**PDF RAG Chatbot**](./Pdf_chatbot.py) | LangChain, PyMuPDF, ChromaDB, SentenceTransformers, Ollama | End-to-end Retrieval-Augmented Generation (RAG) pipeline over PDF documents with semantic chunking, vector search, and grounded question answering. |

---

## 🏗️ Architecture Highlights

### 1. Market Intelligence Research Agent
```
[User Brief] ──► [Intake & Normalize] ──► [Multi-Query Planner (EN/FR/ES/NL)]
                                                    │
    ┌───────────────────────────────────────────────┴───────────────────────────┐
    ▼                                                                           ▼
[Search & Discovery Engine]                                            [World Bank Open Data API]
    │                                                                           │
    └───────────────────────────────┬───────────────────────────────────────────┘
                                    ▼
                        [Evidence Extractor]
                                    │
                                    ▼
                [QC Validator (Grounding & Attribution)]
                                    │
                                    ▼
                    [Analysis & Comparability Engine]
                                    │
                                    ▼
            [21-Section Report Writer & PDF Generator]
```

### 2. Autonomous Coding Agent Loop
```
[Task Description] ──► [Architect Planner]
                             │
                             ▼
     ┌────────────────► [Coder Node] ────► Generates Solution + Unit Tests
     │                       │
     │                       ▼
     │              [Executor Sandbox] ──► Runs Unit Tests in Subprocess
     │                       │
     │                       ▼
     │               [Reviewer Node] ────► Evaluates Correctness & Edge Cases
     │                       │
     └── [Iterate if Fail] ──┴── [Pass / Max Iterations] ──► [Approved Code]
```

### 3. AI Research Agent Workflow
```
[Topic Input] ──► [Planner Node] ──► [Grounded Researcher] ──► [Report Writer] ──► [Markdown Brief]
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- **Python 3.10+**
- **Git**
- *(Optional)* [Ollama](https://ollama.com) for local models (`ollama run gemma3:4b`)
- *(Optional)* [Google Gemini API Key](https://aistudio.google.com/)

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Arbazkhan-ai/Practical-Agentic-AI-projects-using-LangChain-LangGraph-RAG-LLMs-and-AI-Agents.git
cd Practical-Agentic-AI-projects-using-LangChain-LangGraph-RAG-LLMs-and-AI-Agents
```

### Running the Projects

#### 1. Market Intelligence Research Agent
```bash
cd "Market Intelligence Research Agent"
pip install -r requirements.txt
python app/main.py
python generate_pdf.py
```

#### 2. Coding Agent
```bash
cd "Coding Agent"
pip install -r requirements.txt
python app/main.py
```

#### 3. AI Research Agent
```bash
cd "AI Research Agent"
pip install -r requirements.txt
python app/main.py "Future of Multi-Agent Systems in 2026"
```

#### 4. English Speaking Practice Companion
Open [`English Speaking Practice/index.html`](./English%20Speaking%20Practice/index.html) directly in any modern browser (Google Chrome or Microsoft Edge recommended for Web Speech recognition).

#### 5. PDF RAG Chatbot
```bash
pip install langchain langchain-community langchain-chroma langchain-huggingface langchain-ollama pymupdf
python Pdf_chatbot.py [optional_path_to_pdf]
```

---

## 🔒 Security & Data Integrity Standards
- **Three-Tier Attribution:** Strictly distinguishes `[SOURCED FACT]`, `[ECLECTIK-DERIVED CALCULATION]`, and `[AI INTERPRETATION]`.
- **6-Tier Source Quality:** Prioritizes Tier 1 Multilateral and Tier 2 National Statistical agencies over unverified web content.
- **Denominator Preservation:** Maintains exact measurement metrics, observation years, and methodology caveats across multi-market comparisons.
- **Offline & Fallback Resiliency:** All agents support graceful offline evaluation and self-healing execution when API keys or network services are unavailable.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
