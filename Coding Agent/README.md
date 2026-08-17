# 🤖 Coding Agent

An autonomous, multi-step Coding Agent built using **LangGraph**, **Google GenAI / Gemini**, and **Pydantic**.

---

## 🏗️ Architecture & Workflow

The agent uses a cyclic state graph that plans, codes, executes, and reviews iteratively until the solution is approved or max iterations are reached:

```
[START]
   │
   ▼
[Planner Node] ─── Analyzes prompt, determines architecture & edge cases
   │
   ▼
[Coder Node] ───── Writes implementation code and unit tests
   │
   ▼
[Executor Node] ── Runs code & unit tests in an isolated sandbox
   │
   ▼
[Reviewer Node] ── Inspects code, test outcomes, and gives feedback
   │
   ├─► (Approved / Max Iterations) ──► [END]
   │
   └─► (Needs Revisions) ────────────► [Coder Node] (Loop with Feedback)
```

---

## 📁 Directory Structure

```
Coding Agent/
├── .env
├── README.md
└── app/
    ├── __init__.py
    ├── schemas.py      # Pydantic models (CodePlan, CodeReview)
    ├── state.py        # TypedDict state definition
    ├── planner.py      # Architect & planner node
    ├── coder.py        # Code and test generation node
    ├── executor.py     # Sandbox runner for tests
    ├── reviewer.py     # Review and evaluation node
    ├── graph.py        # LangGraph StateGraph orchestration
    └── main.py         # Entry point & execution script
```

---

## 🚀 Getting Started

### 1. Install Dependencies
Make sure your environment has the required packages:
```bash
pip install langgraph langchain-core google-genai python-dotenv pydantic
```

### 2. Configure API Key
Ensure your `.env` contains your Google GenAI key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Run the Agent
```bash
cd "Coding Agent/app"
python main.py
```
