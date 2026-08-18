# 🌴 Market Intelligence Research Agent (Eclectik Engine)

An autonomous, multi-stage **Market Intelligence & Deep Research Agent** built using **LangGraph**, **Google GenAI / Gemini**, **World Bank API**, and **Firecrawl / Web Search**.

Designed to replicate and supercharge the complete n8n **Eclectik Research Intelligence Brief & Engine** pipeline.

---

## 🏗️ Architecture & Pipeline Flow

The research engine operates as an end-to-end directed StateGraph pipeline with rigorous Quality Control (QC) and deterministic synthesis:

```
[START]
   │
   ▼
[1. Intake & Validation] ─── Validates brief, parses questions, applies regional defaults
   │
   ▼
[2. AI Research Planner] ─── Decomposes brief into 15-25 multilingual queries (en, fr, es, nl) with site: domain filters
   │
   ▼
[3. Search & Ingestion] ──── Executes web search/scraping + queries live World Bank API indicators (tourism, GDP, agriculture)
   │
   ▼
[4. Evidence Extractor] ──── Chunks content & extracts verbatim quotes, numeric values, units, and confidence metrics
   │
   ▼
[5. QC & Validation] ─────── Deterministic rule checks (conflicts, dupes, gaps) + AI claim-support verification
   │
   ▼
[6. Synthesis & Analysis] ── Computes statistical multi-year trends, cross-market comparisons, and AI narrative
   │
   ▼
[7. AI Report Writer] ────── Assembles dataset into an evidence-grounded, citation-backed Markdown research report
   │
   ▼
 [END]
```

---

## 🌟 Key Features

1. **Intake & Brief Validation**: Structured parsing of research titles, objectives, questions, market scope, and date ranges.
2. **Multilingual Query Decomposition**: Emits structured search queries across English, French, Spanish, and Dutch targeting authoritative domains (`caricom.org`, `oecs.int`, `fao.org`, `iica.int`, `cepal.org`, `insee.fr`, `cbs.nl`, `worldbank.org`).
3. **Live World Bank Connector**: Directly integrates live macroeconomic and sector indicators (international tourist arrivals `ST.INT.ARVL`, tourism receipts `ST.INT.RCPT.CD`, agriculture % of GDP `NV.AGR.TOTL.ZS`, food production index `AG.PRD.FOOD.XD`, and imports `TM.VAL.MRCH.CD.WT`).
4. **Strict Grounded Evidence Extraction**: Never hallucinates facts; requires verbatim supporting quotes for every finding.
5. **Two-Stage Quality Control (QC)**:
   - *Deterministic checks*: Detects missing evidence, conflicting numbers across sources, duplicate entries, and incomplete fields.
   - *AI Claim-Support evaluation*: Scores evidence support level (`supported`, `partial`, `unsupported`).
6. **Deterministic Analytics**: Automatically calculates multi-year % changes, trends (`increasing`, `decreasing`, `stable`), and cross-market performance comparisons.
7. **Comprehensive Reporting**: Emits formatted Markdown intelligence reports with citation tables, data gap audits, and QC audit caveats.

---

## 📁 Directory Structure

```
Market Intelligence Research Agent/
├── .env                  # API keys (Google Gemini, Firecrawl, OpenAI)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── outputs/              # Generated research intelligence reports
└── app/
    ├── __init__.py
    ├── config.py         # Caribbean coverage registry, authoritative domains, World Bank codes
    ├── schemas.py        # Pydantic models for brief, plan, findings, trends, and reports
    ├── state.py          # TypedDict state for LangGraph
    ├── llm_client.py     # Multi-provider LLM client with JSON mode and fallback
    ├── intake.py         # Brief intake, normalization, and UUID initialization
    ├── planner.py        # AI Research Planner (Multilingual query generator)
    ├── search.py         # Web search, scraping, and tier matching
    ├── world_bank.py     # Live World Bank API indicator fetcher
    ├── extractor.py      # AI Evidence Extractor node
    ├── qc.py             # Rule checks and AI Claim-Support validation node
    ├── analyzer.py       # Deterministic trend & comparative analysis node
    ├── report_writer.py  # Comprehensive Markdown report generator node
    ├── graph.py          # LangGraph StateGraph assembly
    └── main.py           # CLI entry point
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd "Market Intelligence Research Agent"
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
# Optional:
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 3. Run the Research Pipeline

```bash
cd app
python main.py
```
