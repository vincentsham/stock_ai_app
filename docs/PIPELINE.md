# Data Pipeline and Workflow  
**Project:** AI Stock Intelligence System  
**Author:** Vincent Sham  

---

## Overview  

The AI Stock Intelligence System follows a **modular, multi-stage pipeline** that integrates data ingestion, AI-driven analysis, and multi-pillar scoring.  
Each stage is designed for transparency, modularity, and reproducibility — enabling independent development, testing, and optimization of each AI agent and data layer.

---


## 1. Data Ingestion Layer  

### Purpose  
Collects structured and unstructured financial data from multiple APIs and feeds for downstream analysis.

| Component | Description | Data Sources |
|------------|--------------|---------------|
| **Market Data ETL** | Fetches real-time and historical stock or crypto prices. | Yahoo Finance, Twelvedata, CoinCodex |
| **Fundamentals ETL** | Gathers company earnings, balance sheets, and cash flow data. | FMP API, Nasdaq |
| **News ETL** | Retrieves financial headlines, summaries, and metadata. | News API, Benzinga |
| **Event & Catalyst ETL** | Collects information about corporate actions, M&A, or product launches. | Nasdaq, Benzinga |

### Output  
- Stored in **`raw` schema**  
- Standardized fields: `tic`, `date`, `publisher`, `title`, `url`, `content`, `source`

---

## 2. Data Normalization & Storage  

### Purpose  
Transforms raw data into standardized, queryable formats.  
Uses **PostgreSQL with pgvector** for hybrid retrieval (semantic + keyword).

| Schema | Role | Example Tables |
|---------|------|----------------|
| **raw** | Direct data ingestion, unprocessed JSON and text. | `raw.news`, `raw.earnings_transcripts` |
| **core** | Cleaned, validated, and normalized structured data. | `core.financials`, `core.earnings`, `core.transcripts` |
| **mart** | Aggregated features, model results, and pillar scores. | `mart.stock_scores`, `mart.ai_ratings` |

---

## 3. AI Agent Layer  

### Purpose  
Analyzes different dimensions of company performance using domain-specific AI agents.

| Agent | Description | Key Output |
|--------|--------------|-------------|
| **News Agent** | Classifies headlines by event type, sentiment, and market impact. | Category, sentiment, time horizon, magnitude |
| **Earnings Transcript Agent** | Analyzes tone, management confidence, and risk mentions. | Risk signals, guidance tone, qualitative summary |
| **Financial Report Agent** | Extracts financial KPIs from statements and ratios. | Growth metrics, profitability, leverage ratios |
| **Analyst Forecast Agent** | Aggregates analyst PTs, upgrades/downgrades, and revisions. | Consensus targets, dispersion, directionality |
| **Market Trend Agent** | Captures technical momentum, volume patterns, and volatility. | Momentum indicators, trend classification |

All agents write structured JSON outputs into the **`core` or `mart`** schema, conforming to Pydantic data models.

---

## 4. Feature Aggregation Layer  

### Purpose  
Combines agent outputs into unified, time-aligned feature sets for scoring and classification.

| Process | Description |
|----------|-------------|
| **Temporal Alignment** | Synchronizes agent results by fiscal date and ticker. |
| **Feature Normalization** | Scales metrics using z-score, percentile, or min–max normalization. |
| **Dimensional Tagging** | Maps each feature to its corresponding pillar and sub-pillar. |
| **Feature Versioning** | Tracks data and model versions for reproducibility. |

Output: aggregated feature table (e.g., `mart.features_combined`).

---

## 5. Stock Type Classification  

### Purpose  
Groups companies by **structural and behavioral profiles** to enable type-specific comparisons.

| Stage | Description |
|--------|-------------|
| **Archetype Identification** | Growth, Value, Defensive, Cyclical, High-Margin, Pre-Profit, etc. |
| **Subtype Labeling** | Adds refinement (e.g., Hypergrowth, R&D-Led, Quality Value). |
| **Tagging System** | Thematic and situational tags (e.g., AI_Beneficiary, Founder_Led). |

The classification is used for **peer benchmarking** and **score normalization** in the next stage.

---

## 6. Multi-Pillar Scoring Engine  

### Purpose  
Evaluates each company across structured, interpretable dimensions.

| Pillar | Example Sub-Pillars | Description |
|---------|---------------------|--------------|
| **Growth** | Revenue & EPS Growth, Market Share Gain | Measures business expansion and reinvestment. |
| **Profitability** | Margins, ROIC, Efficiency | Evaluates earnings quality and cost structure. |
| **Quality & Risk** | Balance Sheet, Stability, Risk Exposure | Assesses resilience and downside protection. |
| **Valuation** | Absolute & Relative Multiples | Compares price levels versus fundamentals and peers. |
| **Momentum** | Price Action, Volume Flow, Catalyst Reaction | Captures technical strength and sentiment. |
| **Execution** | Earnings Surprise, Tone, Guidance | Evaluates management performance and strategy follow-through. |

The scoring process integrates:
- **Trend Awareness:** Detects improving or deteriorating metrics.  
- **Peer Normalization:** Adjusts for sector and stock type context.  
- **Weighted Aggregation:** Produces composite scores per pillar and overall rating.

---

## 7. AI Rating & Price Target Generation  

### Purpose  
Synthesizes quantitative and qualitative insights into **AI-generated ratings and PTs**.

| Component | Description |
|------------|-------------|
| **Rating Model** | Classifies stock as Buy/Hold/Sell or outputs numerical score (0–100). |
| **Price Target Estimation** | Uses valuation models and peer metrics to derive AI PTs. |
| **Rationale Generation** | Generates textual explanation citing key contributing pillars. |

Output tables:  
- `mart.ai_ratings`  
- `mart.price_targets`  

---

## 8. Web Application Layer (Planned)  

### Purpose  
Provides an interactive interface for users to explore insights, scores, and reports.

| Component | Technology | Function |
|------------|-------------|-----------|
| **Backend API** | FastAPI | Serves data endpoints for scores, classifications, and analysis. |
| **Frontend** | Next.js / React | Visualizes company dashboards, score breakdowns, and PT comparisons. |
| **Visualization Libraries** | Plotly / Recharts | Graphical analytics and multi-pillar visualization. |

---

## 9. Summary of Data Flow  

| Stage | Input | Output | Destination |
|--------|--------|---------|--------------|
| **1. Ingestion** | APIs, feeds | Raw JSON/text | `raw` schema |
| **2. Normalization** | Raw data | Structured tables | `core` schema |
| **3. Agent Analysis** | Core tables | JSON insights | `core` / `mart` |
| **4. Feature Aggregation** | Agent outputs | Unified feature table | `mart.features_combined` |
| **5. Classification** | Features | Stock types, subtypes, tags | `mart.classifications` |
| **6. Scoring** | Aggregated features | Pillar & total scores | `mart.stock_scores` |
| **7. AI Ratings & PTs** | Scores + qualitative data | Rating, rationale, price target | `mart.ai_ratings` |
| **8. Web Output** | API responses | Dashboard & reports | Frontend layer |

---
