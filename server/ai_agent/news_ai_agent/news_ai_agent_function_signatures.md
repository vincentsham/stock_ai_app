# State Model & Function Signatures — Two-Stage News Agent (LangGraph Framework)

This document defines the **state model**, **function signatures**, and **LangGraph framework integration** for implementing the two-stage LLM news analysis pipeline. It complements the main pipeline spec `two_stage_news_agent_for_copilot.md`.

---

## ⚙️ Framework Overview — LangGraph

The system runs under **LangGraph**, where each function corresponds to a node in a graph:

```
Input → Stage1 Node → Filter (Noise) → Stage2 Node → Filter (Minor) → Output Node
```

### Nodes

- **Stage1 Node**: Classifies category & event\_type.
- **Stage2 Node**: Estimates impact, duration, and sentiment.
- **Validation Node (optional)**: Ensures final JSON consistency.

### Graph Behavior

- Each node receives a `News` state and returns an updated version.
- The state propagates through edges unless dropped (e.g., `noise`, `minor`).
- Use `ToolNode` or `LLMNode` types for Stage 1 and Stage 2.
- Transitions are conditionally routed using `if` filters or control nodes.

\--- & Function Signatures — Two-Stage News Agent

This document defines the **state model** and **function signatures** for implementing the two-stage LLM news analysis pipeline. It complements the main pipeline spec `two_stage_news_agent_for_copilot.md`.

---

## 🧩 State Model

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

Category = Literal["fundamental","market_perception","technical","noise"]
TimeHorizon = Literal["short_term","mid_term","long_term"]
ImpactMag = Literal["minor","moderate","major"]
Sentiment = Literal["positive","neutral","negative"]

class News(BaseModel):
    # Inputs
    ticker: str
    headline: str
    summary: str
    publisher: str
    publish_date: str  # ISO 8601 with time, e.g., "2025-10-03 12:15:05"

    # Stage 1 outputs
    category: Optional[Category] = None
    event_type: Optional[str] = None

    # Stage 2 outputs
    time_horizon: Optional[TimeHorizon] = None
    duration: Optional[str] = None
    impact_magnitude: Optional[ImpactMag] = None
    affected_dimensions: Optional[List[Literal[
        "revenue","profit","cash","cost","risk","technology","sentiment"
    ]]] = None
    sentiment: Optional[Sentiment] = None

```

---

## ⚙️ Function Signatures

### Stage 1 — Classification

```python
def stage1(state: News) -> dict:
    """Run Stage 1 LLM classifier. 
    Input: News (headline, summary, etc.)
    Output: {"category": <str>, "event_type": <str>} 
    Drops if category == 'noise'.
    """
    # Inputs include ticker, headline, summary, publisher, and publish_date
    # Outputs include category and event_type
```

### Stage 2 — Impact & Sentiment Analysis

```python
def stage2(state: News) -> dict:
    """Run Stage 2 LLM analysis using Stage 1 outputs.
    Input: News + Stage 1 results
    Output: {
        "time_horizon": <str>,
        "duration": <str>,
        "impact_magnitude": <str>,
        "affected_dimensions": <list>,
        "sentiment": <str>
    }
    """
    # Inputs include ticker, headline, summary, publisher, publish_date, category, and event_type
    # Outputs include time_horizon, duration, impact_magnitude, affected_dimensions, and sentiment
    # Note: No filtering based on impact_magnitude
```

### JSON Validation

```python
def validate_json(state: News) -> bool:
    """Validate that all populated fields follow schema rules.
    - Enforce lowercase enums and valid field types.
    - Ensure `duration` matches the expected range for `time_horizon`.
    - Return True if valid, False otherwise.
    """
    # Validation ensures strict adherence to the schema defined in the News model
    # Note: No highlighting based on impact_magnitude
```

---

## 🧠 Usage Example

```python
news = News(
    ticker="TSLA",
    headline="Tesla posts record Q3 deliveries",
    summary="Tesla delivered 435,000 vehicles in Q3 2025, exceeding expectations.",
    publisher="Reuters",
    publish_date="2025-10-03 12:15:05"
)

# Run classification chain
s1 = stage1(news)
if s1 and s1.get("category") != "noise":
    s2 = stage2(news)
    if s2:
        news = news.copy(update={**s1, **s2})
        assert validate_json(news)
```



