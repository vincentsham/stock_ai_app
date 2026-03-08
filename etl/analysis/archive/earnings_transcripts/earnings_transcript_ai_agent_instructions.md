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

### Node/Branch Structure

```
input
→ fanout (parallel branch)
    ├─ past_retriever_node → past_analysis_node
    ├─ future_retriever_node → future_analysis_node
    └─ risk_retriever_node → risk_analysis_node → queries_powered_by_llm → risk_response_retriever_node → risk_response_analysis_node
→ merge (implicit at END)
```

### Core Rules

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
from states import MergedState

# @copilot: retrieve top-K transcript chunks for a given analysis type ("past", "future", "risk", "risk_response")
def retriever(state: MergedState, type: Literal["past", "future", "risk", "risk_response"]) -> dict:
    ...

# @copilot: call LLM with the appropriate system prompt and context for the given analysis type
def analysis_node(state: MergedState, type: Literal["past", "future", "risk", "risk_response"], history: Optional[Literal["past", "future", "risk", "risk_response"]] = None) -> dict:
    ...

# @copilot: use LLM to generate risk response queries based on risk analysis output
def queries_powered_by_llm(state: MergedState) -> dict:
    ...

# Partial functions for each node type (see nodes.py for details)
past_analysis_node = partial(analysis_node, type='past')
future_analysis_node = partial(analysis_node, type='future')
risk_analysis_node = partial(analysis_node, type='risk')
risk_response_analysis_node = partial(analysis_node, type='risk_response', history='risk')

past_retriever_node = partial(retriever, type='past')
future_retriever_node = partial(retriever, type='future')
risk_retriever_node = partial(retriever, type='risk')
risk_response_retriever_node = partial(retriever, type='risk_response')
```

| Function                  | Input         | Output         | Description |
|---------------------------|---------------|----------------|-------------|
| `retriever`               | `MergedState`, type | dict      | Retrieves transcript segments for an aspect |
| `analysis_node`           | `MergedState`, type | dict      | LLM-based analysis for the given aspect |
| `queries_powered_by_llm`  | `MergedState` | dict           | LLM-based query generation for risk response |

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
    company_info: CompanyInfo
    past_retriever: Optional[RetrieverState] = None
    future_retriever: Optional[RetrieverState] = None
    risk_retriever: Optional[RetrieverState] = None
    risk_response_retriever: Optional[RetrieverState] = None
    past_analysis: Optional[PastState] = None
    future_analysis: Optional[FutureState] = None
    risk_analysis: Optional[RiskState] = None
    risk_response_analysis: Optional[RiskResponseState] = None
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
from nodes import (
    past_retriever_node, future_retriever_node, risk_retriever_node,
    past_analysis_node, future_analysis_node, risk_analysis_node,
    risk_response_analysis_node, risk_response_retriever_node,
    queries_powered_by_llm
)
from states import merged_state_factory

# @copilot: simulate full pipeline for TSLA Q2 2025
state = merged_state_factory(
    tic="TSLA",
    company_name="Tesla, Inc.",
    industry="Automotive",
    sector="Consumer Discretionary",
    company_description="Tesla, Inc. is a leading electric vehicle and clean energy company.",
    fiscal_year=2025,
    fiscal_quarter=2,
    earnings_date="2025-07-24"
)

# Run the graph (see graph.py for orchestration)
result = app.invoke(state)

print("===========past===============")
print(result['past_analysis'])
print("===========future===============")
print(result['future_analysis'])
print("===========risk===============")
print(result['risk_analysis'])
print("===========risk response===============")
print(result['risk_response_analysis'])
```

---

## 🗂 Project Layout

```
earnings_ai_agent/
│
├── states.py                # Pydantic models and state factory
├── prompts.py               # LLM prompt templates and queries
├── nodes.py                 # Node logic (retrievers, analyzers, query generation)
├── graph.py                 # LangGraph flow definition and orchestration
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

