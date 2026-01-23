# Data Pipeline and Workflow
**Project:** Stock AI App
**Status:** Active
**Pipeline Orchestration:** Python scripts triggered via Shell scripts

---

## Overview

The Stock AI App data pipeline utilizes a **Linear ETL (Extract-Transform-Load) + Analysis** architecture. It is designed to progressively refine data from raw API responses into structured, AI-enriched insights served to the web application.

**Data Flow:**
`External APIs` → **[Extract]** → `raw` Schema → **[Load]** → `core` Schema → **[Transform/Analysis]** → `core` (Enriched) → **[Publish]** → `mart` Schema

---

## 1. Extract (Ingestion)
**Directory**: `etl/extract/`  
**Schema Target**: `raw.*`

### Purpose
Responsible for connecting to external data providers, handling rate limits, fetching data, and storing it "as-is" in the database.

*   **Process**:
    *   Fetches data from `FMP`, `Yahoo Finance`, `CoinCodex`, etc.
    *   Hashes raw JSON blobs for lineage and change detection (`raw_json_sha256`).
    *   Inserts new records into the `raw` schema (e.g., `raw.news`, `raw.earnings`, `raw.stock_prices`).
*   **Key Scripts**:
    *   `extract/news/extract_news_fmp.py`: Fetches latest news.
    *   `extract/stocks/extract_stock_ohlcv_daily_yf.py`: Fetches daily price data.
    *   `extract/earnings/extract_earnings.py`: Fetches earnings calendars and actuals.

---

## 2. Load (Normalization & Standardization)
**Directory**: `etl/load/`  
**Schema Target**: `core.*`

### Purpose
Reads raw data, cleans it, standardizes formats, and strictly validates it for downstream use.

*   **Process**:
    *   **Fiscal Alignment**: Maps fiscal quarters to calendar quarters (e.g., `fiscal_year` vs `calendar_year`).
    *   **Deduplication**: Ensures unique records per ticker/date using hash keys.
    *   **Structure**: Moves data from `raw.*` JSON blobs into typed columns in `core.*` (e.g., `core.earnings`, `core.stock_profiles`).
    *   **Embedding Prep**: Chunks text (transcripts) and prepares them for embedding (if applicable).
*   **Key Scripts**:
    *   `load/earnings/load_earnings.py`: Standardizes earnings reports.
    *   `load/earnings/load_earnings_calendar_defeatbeta.py`: Manages forward-looking calendar.

---

## 3. Transform (Metrics Calculation)
**Directory**: `etl/transform/`  
**Schema Target**: `core.*` / `mart.*` (Intermediate)

### Purpose
Calculates quantitative ratios, growth rates, and statistical percentiles on top of the clean `core` data.

*   **Process**:
    *   **Financial Ratios**: Computes PE, PS, ROE, Margins based on `core.financials`.
    *   **Growth Metrics**: Calculates YoY growth, 3Y/5Y CAGRs for Revenue, EPS, FCF.
    *   **Percentiles**: Ranks companies against peers to generate scoring inputs.
*   **Key Scripts**:
    *   `transform/earnings/main.py`: Earnings-specific transformations.
    *   `transform/metrics/`: Calculation of Valuation, Profitability, and Efficiency metrics.

---

## 4. Analysis (AI Agents)
**Directory**: `etl/analysis/`  
**Schema Target**: `core.*_analysis`

### Purpose
Runs advanced AI agents (LangGraph/LLMs) to extract semantic meaning from unstructured text.

*   **Process**:
    *   **News Agent**: Reads `core.news`, classifies events, assigns sentiment/impact scores, and writes to `core.news_analysis`.
    *   **Earnings Agent**: Reads `core.earnings_transcripts`, analyzes management tone, risks, and guidance, writing to `core.earnings_transcript_analysis`.
    *   **Catalyst Agent**: Identifies and links catalysts to stock entities.
*   **Key Scripts**:
    *   `analysis/news/main.py`: processing news stream.
    *   `analysis/earnings_transcripts/main.py`: analyzing earnings calls.
    *   `analysis/analysts/main.py`: summarizing analyst consensus.

---

## 5. Publish (Serving Layer)
**Directory**: `etl/publish/`  
**Schema Target**: `mart.*`

### Purpose
The final stage that aggregates all insights into consumer-ready "Data Mart" tables. This layer is optimized for the Web App's query patterns.

*   **Process**:
    *   **Scoring**: Aggregates normalized metrics into Pillar Scores (Growth, Value, etc.) and Total Scores.
    *   **Versioning**: Snapshots data with `as_of_date` to allow historical point-in-time analysis.
    *   **Denormalization**: Flattens complex relationships into single tables for fast UI loading.
*   **Key Scripts**:
    *   `publish/publish_stock_profiles.py`: Pushes canonical profiles.
    *   `publish/publish_stock_scores.py`: Calculates and publishes final 0-100 scores.
    *   `publish/run_publish.sh`: Orchestrates the sync to production tables.

---

## 6. Orchestration
**Directory**: `etl/` (Root scripts)

The pipeline is triggered via shell scripts that manage dependencies and logging:
*   `extract/run_extract.sh` → Runs daily ingestion.
*   `load/run_load.sh` → Normalizes raw data.
*   `transform/run_transform.sh` → Updates computed metrics.
*   `analysis/run_analysis.sh` → Triggers AI agents.
*   `publish/run_publish.sh` → Pushes updates to the web app DB (`mart`).

All logs are stored in `logs/` with daily rotation.
