# Two-Stage News Analysis Agent — LangGraph Implementation Spec

This document defines a LangGraph-based architecture for the two-stage AI news analysis agent. It combines the Stage 1 (Category/Event) and Stage 2 (Impact/Duration/Sentiment) modules into a node-based workflow.

---

## ⚙️ Framework Integration — LangGraph

This agent operates under the **LangGraph framework**, where each stage is implemented as a node that mutates a shared `News` state.

### Graph Flow

```
Input Node (data from raw.news) 
  → Stage 1 Node (category, event_type) → Filter (noise)
    → Stage 2 Node (time_horizon, duration, impact_magnitude, affected_dimensions, sentiment) → Filter (minor)
      → Output Node (data loaded into core.news_analysis)
```

- The `News` state (defined in `news_state_model_and_functions.md`) propagates between nodes.
- Use `ConditionalEdge` for routing logic.
- All outputs **lowercase JSON**; strict schema validation with one auto-retry on invalid JSON.

---


### Input and Output Locations

- **Input Location**: The input data is sourced from the `raw.news` table in the database. This table contains raw news items with fields such as `ticker`, `headline`, `summary`, `publisher`, `publish_date`, and `url`.
- **Output Location**: The processed data is stored in the `core.news_analysis` table. This table includes additional fields such as `category`, `event_type`, `time_horizon`, `duration`, `impact_magnitude`, `affected_dimensions`, and `sentiment`.

---

## 1) Input Contract

Each news item must provide:

```json
{
  "ticker": "TSLA",
  "headline": "Tesla posts record Q3 deliveries",
  "summary": "Tesla delivered 435,000 vehicles in Q3 2025, exceeding expectations and marking an all-time high.",
  "publisher": "reuters",
  "publish_date": "2025-10-03 12:15:05",
  "url": "https://www.reuters.com/tesla-record-q3-deliveries"
}
```

Notes:

- The input data is sourced from the `raw.news` table.
- `publish_date` is informational context only; do not infer future events.
- `summary` should be 2–4 factual sentences.

---

## 2) Stage 1 — News Category & Event Type Classifier

#### System Message

```text
System Message: Stage 1 — News Category & Event Type Classifier
---------------------------------------------------------------
You are a financial news classification agent. Analyze a headline + short summary and return only JSON with `category` and `event_type`.

Decision Tree (apply in order)
1) Verifiable business fact/event (earnings, operations, regulation, leadership, M&A, filings, alt data)? → fundamental
2) Opinion/perception without new facts (analyst calls, investor letters, media narratives, PR controversies, social buzz)? → market_perception
3) Market structure/price/flows/signals (charts, volume, options, ETFs)? → technical
4) Low-value/irrelevant/duplicate/clickbait (no new insight, generic PR, price recap, unverified rumor)? → noise (default if none apply)

Event Types
- fundamental: [earnings_guidance, mna, capital_action, regulatory_legal, leadership, operations, customer_contract, sector_macro, other]
- market_perception: [analyst_action, media_narrative, investor_letter, pr_issue, other]
- technical: [price_pattern, options_flow, volume_flow, etf_flow, other]
- noise: [other]

Tie-Break Rules
- Any new verifiable fact ⇒ fundamental (even if opinions present).
- Price recaps are noise (not technical).
- Pick the most specific `event_type`.
- If multiple companies, focus on the headline’s main subject.

Output Format (required)
Return valid JSON only:
{
  "category": "choose one from ['fundamental','market_perception','technical','noise']",
  "event_type": "choose one valid option for that category"
}
Do not add extra keys or commentary.
```

#### Prompt Template

```text
You are classifying a piece of company news for the ticker {ticker}.
Inputs:
- Headline: {headline}
- Summary: {summary}
- Ticker: {ticker}
- Publisher: {publisher}
- Publish Date: {publish_date}
Return only valid JSON with:
{
  "category": "one of ['fundamental','market_perception','technical','noise']",
  "event_type": "one valid option from the list for that category"
}
```

### Stage-1 Output Schema

```json
{
  "category": "fundamental | market_perception | technical | noise",
  "event_type": "string (constrained by category)"
}
```

---

## 3) Stage 2 — News Impact, Duration & Sentiment Classifier

#### System Message

```text
System Message: Stage 2 — News Impact, Duration & Sentiment Classifier
---------------------------------------------------------------
You are a financial news impact analysis agent. Analyze headline + summary with Stage-1 labels and return only JSON.

Fields
{
  "time_horizon":  "short_term | mid_term | long_term",
  "duration": "specific expected duration (e.g., '2 weeks','3 months','1 year')",
  "impact_magnitude": "minor | moderate | major",
  "affected_dimensions": ["revenue","profit","cash","cost","risk","technology","sentiment"],
  "sentiment": "positive | neutral | negative"
}

Horizon Definitions
- short_term: ≤ 1 week (immediate trading reaction)
- mid_term: ≤ 3 months (near-term/next quarter)
- long_term: ≥ 3 months (strategic/structural/regulatory)

Impact Magnitude Rules
- major: Company-wide or structural change — long-term effect on revenue, operations, or valuation.
         Examples: M&A, regulatory decisions, major contracts, leadership change, or product breakthroughs.
- moderate: Meaningful but narrower impact — affects a business segment, region, or short-term results.
            Examples: analyst actions, temporary supply issues, product delays, or quarterly earnings surprises.
- minor: Small, local, or speculative — minimal or transient effect on operations or outlook.
         Examples: local partnerships, small-scale events, or rumors without confirmed follow-up.

Affected Dimensions (pick up to 3)
[revenue, profit, cash, cost, risk, technology, sentiment]

Sentiment
- positive: favorable for business/perception
- neutral: factual or mixed
- negative: unfavorable or risk-increasing

Output Format (required)
Return valid JSON only with the exact fields and values above; no extra keys or commentary.
```

#### Prompt Template

```text
You are analyzing a piece of company news for the ticker {ticker} to determine its impact, duration, and sentiment.
Inputs:
- Headline: {headline}
- Summary: {summary}
- Ticker: {ticker}
- Publisher: {publisher}
- Publish Date: {publish_date}
- Category: {category}
- Event Type: {event_type}
Return only valid JSON with:
{
  "time_horizon":  "short_term | mid_term | long_term",
  "duration": "specific expected duration (e.g., '2 weeks','3 months','1 year')",
  "impact_magnitude": "minor | moderate | major",
  "affected_dimensions": ["revenue","profit","cash","cost","risk","technology","sentiment"],
  "sentiment": "positive | neutral | negative"
}
```

### Stage-2 Output Schema

```json
{
  "time_horizon": "short_term | mid_term | long_term",
  "duration": "string (e.g., '2 weeks','3 months','1 year')",
  "impact_magnitude": "minor | moderate | major",
  "affected_dimensions": ["revenue","profit","cash","cost","risk","technology","sentiment"],
  "sentiment": "positive | neutral | negative"
}
```

---

## 4) Control Flow & Guardrails (LangGraph Version)

Instead of procedural function calls, define a LangGraph pipeline:

```python
from langgraph.graph import Graph

graph = Graph()
graph.add_node("stage1", stage1)
graph.add_node("stage2", stage2)

graph.add_edge("stage1", "stage2", condition=lambda s: s.category != "noise")
graph.add_edge("stage2", "output", condition=lambda s: s.impact_magnitude != "minor")
```

- Each node mutates the same `News` state.
- Transitions are conditional.
- `validate_json()` runs after each stage.

---

## 5) End-to-End Example

**Input**

```json
{
  "ticker": "ORCL",
  "headline": "Oracle signs $10B multi-year deal with OpenAI",
  "summary": "Oracle will supply cloud infrastructure to OpenAI in a long-term, $10B partnership.",
  "publisher": "reuters",
  "publish_date": "2025-10-03 12:15:05"
}
```

**Stage 1 →**

```json
{ "category": "fundamental", "event_type": "customer_contract" }
```

**Stage 2 →**

```json
{
  "time_horizon": "long_term",
  "duration": "5 years",
  "impact_magnitude": "major",
  "affected_dimensions": ["revenue", "technology"],
  "sentiment": "positive"
}
```

**Final Output →**

```json
{
  "ticker": "ORCL",
  "headline": "Oracle signs $10B multi-year deal with OpenAI",
  "summary": "Oracle will supply cloud infrastructure to OpenAI in a long-term, $10B partnership.",
  "publisher": "reuters",
  "publish_date": "2025-10-03 12:15:05",
  "category": "fundamental",
  "event_type": "customer_contract",
  "time_horizon": "long_term",
  "duration": "5 years",
  "impact_magnitude": "major",
  "affected_dimensions": ["revenue", "technology"],
  "sentiment": "positive"
}
```

---

## 6) Implementation Notes

- Use **LangGraph** nodes to define the workflow.
- Keep `temperature` between `0.0–0.2`.
- Use schema validation: Pydantic.
- Log prompt and truncated responses for debugging.
