# 🧠 Three-Stage Earnings Transcript Analysis Agent — LangGraph Implementation Spec (v4, Integrated for Copilot)

This document merges the **original project specification** and the **developer-focused Copilot instruction guide**, creating a single, detailed, and AI-friendly build reference for your `earnings_transcript_ai_agent` project.

---

## ⚙️ Overview

The agent is a **LangGraph-based pipeline** that analyzes **earnings transcripts** in three analytical dimensions:

1. **Past Performance**
2. **Future Outlook & Strategy**
3. **Risk & Uncertainty Disclosure**

Each aspect runs independently with its own retriever and analyzer node.\
The system uses **hybrid RAG** (pgvector cosine similarity) over a **PostgreSQL** corpus containing transcript chunks.

All node logic, state models, and prompts are designed to be **Copilot-compatible** — enabling automatic code generation and consistent schema adherence.

---

## 🧩 Execution Flow (LangGraph)

### Order of Nodes

```
input
→ past_retriever → past_analysis
→ outlook_retriever → future_analysis
→ risk_retriever → risk_analysis
→ merge_results → output
```

### Core Rules

- **Sequential execution only** — deterministic batch-safe design.
- **Fail-fast policy** — any failed node stops the pipeline.
- **No retries** in v1 (handled externally in orchestration layer).
- **Empty retrieval** = error (no fallback).
- **LLM configuration:**
  - `model = gpt-5`
  - `temperature = 0`
  - `max_tokens` left default.

---

## 🧱 Node Function Signatures (`nodes.py`)

All node signatures follow strict type contracts and include inline **Copilot task hints** for auto-generation.

```python
from states import RetrievalState, PastState, FutureState, RiskState, MergedState

# @copilot: implement retrieval logic using psycopg2 or asyncpg
# Fetch top-K transcript chunks using pgvector cosine similarity
# Return dict containing 'chunks' and 'chunks_score'
def retriever(state: RetrievalState) -> dict:
    pass

# @copilot: call LLM with PAST_PROMPT, validate JSON → PastState
# Return dict following PastState schema
def past_analysis(state: PastState) -> dict:
    pass

# @copilot: call LLM with FUTURE_PROMPT, validate JSON → FutureState
# Return dict following FutureState schema
def future_analysis(state: FutureState) -> dict:
    pass

# @copilot: call LLM with RISK_PROMPT, validate JSON → RiskState
# Return dict following RiskState schema
def risk_analysis(state: RiskState) -> dict:
    pass

# @copilot: merge validated PastState, FutureState, and RiskState
# Return MergedState JSON-serializable object
def merge_results(past: PastState, future: FutureState, risk: RiskState) -> MergedState:
    merged = MergedState(past=past, future=future, risk=risk)
    return merged
```

| Function          | Input            | Output                             | Description                                          |
| ----------------- | ---------------- | ---------------------------------- | ---------------------------------------------------- |
| `retriever`       | `RetrievalState` | dict with `chunks`, `chunks_score` | Retrieves transcript segments for an aspect.         |
| `past_analysis`   | `PastState`      | dict                               | LLM-based factual summary of historical performance. |
| `future_analysis` | `FutureState`    | dict                               | LLM-based extraction of guidance and catalysts.      |
| `risk_analysis`   | `RiskState`      | dict                               | LLM-based detection of disclosed risks.              |
| `merge_results`   | 3 State objects  | `MergedState`                      | Combines all outputs into one unified JSON.          |

---

## 🧾 Input Contract

**Agent Inputs:**

- `tic` (ticker, str)
- `fiscal_year` (int)
- `fiscal_quarter` (int)

**Optional Metadata:**

- `company_name`, `industry`, `sector`, `description`, `earnings_date`

**Retrieval Data Source:**

- PostgreSQL table: `core.earnings_transcript_chunks`
- Columns: `(tic, fiscal_year, fiscal_quarter, chunk, embedding)`
- Average chunk length: \~512 tokens

**Retrieval Policy:**

- Top-K = 5 per node.
- Vector similarity only (no BM25 fallback in v1).
- Fail-fast on 0 results.

---

## 🧱 State Definitions (`states.py`)

### RetrievalState

```python
class RetrievalState(BaseModel):
    tic: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    company_description: Optional[str] = None
    fiscal_year: int
    fiscal_quarter: int
    earnings_date: Optional[str] = None
    top_k: int = 5
    chunks: List[str] = Field(default_factory=list)
    chunks_score: List[float] = Field(default_factory=list)
```

### PastState

```python
class PastState(BaseModel):
    sentiment: Optional[Tri] = None
    durability: Optional[Horizon] = None
    performance_factors: List[str] = []
    summary: Optional[str] = None
```

### FutureState

```python
class FutureState(BaseModel):
    guidance_direction: Optional[Tri] = None
    revenue_outlook: Optional[Tri] = None
    earnings_outlook: Optional[Tri] = None
    margin_outlook: Optional[Tri] = None
    cashflow_outlook: Optional[Tri] = None
    growth_acceleration: Optional[Tri] = None
    future_outlook_sentiment: Optional[Tri] = None
    catalysts: List[str] = []
    summary: Optional[str] = None
```

### RiskState

```python
class RiskState(BaseModel):
    risk_mentioned: Optional[Binary01] = None
    risk_impact: Optional[Tri] = None
    risk_time_horizon: Optional[Horizon] = None
    risk_factors: List[str] = []
    summary: Optional[str] = None
```

### MergedState

```python
class MergedState(BaseModel):
    past: PastState
    future: FutureState
    risk: RiskState
```

---

## 🧠 Prompt Configuration (`prompts.py`)

Each analysis node calls a dedicated system prompt. Copilot should use `ChatOpenAI` or equivalent LangChain model with `temperature=0`.

Example:

```python
PAST_PROMPT = """
System Message: You are a financial analyst analyzing past performance.
Use the transcript excerpts to extract key operational results, sentiment, and performance factors.
Return valid JSON that exactly matches the PastState schema.

Input:
{chunks}
"""
```

Prompts for `FUTURE_PROMPT` and `RISK_PROMPT` follow the same pattern.

---

## 🔍 Retrieval & Scoring Logic

**SQL template for retriever node:**

```sql
SELECT chunk, embedding
FROM core.earnings_transcript_chunks
WHERE tic = %(tic)s
  AND fiscal_year = %(fiscal_year)s
  AND fiscal_quarter = %(fiscal_quarter)s
ORDER BY embedding <=> %(query_vector)s
LIMIT 5;
```

- **Similarity metric:** cosine (pgvector)
- **If zero rows:** raise exception
- **Output:** dict containing `chunks`, `chunks_score`

---

## 🧩 Merge Behavior

- No score computation or weighting.
- Simply package all validated sub-results into a single nested JSON.

```python
{
  "tic": "AAPL",
  "fiscal_year": 2025,
  "fiscal_quarter": 3,
  "past": {...},
  "future": {...},
  "risk": {...}
}
```

---

## 🧪 Test Example

```python
from nodes import retriever, past_analysis, future_analysis, risk_analysis, merge_results
from states import RetrievalState, PastState, FutureState, RiskState

# @copilot: simulate full pipeline
retrieved = retriever(RetrievalState(tic="AAPL", fiscal_year=2025, fiscal_quarter=3))

past = past_analysis(PastState(**retrieved))
future = future_analysis(FutureState(**retrieved))
risk = risk_analysis(RiskState(**retrieved))

merged = merge_results(past, future, risk)
print(merged.model_dump_json(indent=2))
```

---

## 🗂 Project Layout

```
earnings_ai_agent/
│
├── states.py                # Pydantic models
├── prompts.py               # LLM prompt templates
├── nodes.py                 # Node logic (retrievers + analyzers)
├── graph.py                 # LangGraph flow definition
├── main.py                  # CLI or batch entry
└── docs/
    └── earnings_transcript_ai_agent_spec.md
```

---

## 🦭 Future Roadmap

-

---

### ✅ Summary

This integrated doc ensures Copilot can:

- Auto-generate retrieval, analysis, and merge functions.
- Maintain schema adherence with `Pydantic` validation.
- Use explicit inline hints for deterministic, error-free code.
- Follow consistent file layout and naming conventions.

> 🧩 **Goal:** Serve as the single source of truth for both human developers and Copilot code generation.

