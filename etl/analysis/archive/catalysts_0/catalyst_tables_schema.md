# Catalyst Tracking Schema

This document defines the final database schema for the **Catalyst Tracking System**, including the following tables:

- `core.catalyst_master` — canonical catalog of catalysts
- `core.catalyst_daily` — daily (hot-lane) extracted mentions
- `core.catalyst_weekly` — weekly curated and deduplicated mentions

All three schemas are aligned and designed for interpretability, extensibility, and analytical clarity.

---

## Table: `core.catalyst_master`

```sql
CREATE TABLE IF NOT EXISTS core.catalyst_master (
  catalyst_id      UUID PRIMARY KEY,
  tic              VARCHAR(10),
  date             DATE,
  catalyst_type    VARCHAR(64),
  title            TEXT,
  summary          TEXT,
  evidence         TEXT,
  lifecycle_stage  VARCHAR(20),
  sentiment        SMALLINT,
  time_horizon     SMALLINT,
  impact_magnitude SMALLINT,
  certainty        VARCHAR(20),
  impact_area      VARCHAR(32),

  mention_count    INTEGER DEFAULT 1,
  urls      TEXT[] DEFAULT '{}'
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now(),

);
```

### Purpose
- Serves as the **canonical record** for each distinct catalyst.
- Consolidates all mentions from transcripts, filings, and news.
- Updated as new mentions reinforce, update, or withdraw catalysts.

### Key Fields
| Column | Description |
|---------|-------------|
| `catalyst_id` | UUID identity key. |
| `tic` | Stock ticker symbol. |
| `catalyst_type` | Event type, e.g. guidance change, product launch, M&A, etc. |
| `state` | Lifecycle stage (announced, updated, withdrawn, realized). |
| `direction` | -1 negative, 0 neutral, 1 positive. |
| `impact_area` | Which business pillar is affected (revenue, profitability, cashflow, etc.). |
| `certainty_class` | Confidence level: confirmed / planned / rumor / denied. |
| `magnitude_class` | Scale: minor / moderate / major / transformational. |

---

## Table: `core.catalyst_versions`

```sql
CREATE TABLE IF NOT EXISTS core.catalyst_versions (
  version_id       UUID PRIMARY KEY,
  catalyst_id      UUID NOT NULL REFERENCES core.catalyst_master(catalyst_id)
                   ON DELETE CASCADE,

  tic              VARCHAR(10),
  date             DATE,
  catalyst_type    VARCHAR(64),
  title            TEXT,
  summary          TEXT,
  evidence         TEXT,
  lifecycle_stage  VARCHAR(20),
  sentiment        SMALLINT,
  time_horizon     SMALLINT,
  impact_magnitude SMALLINT,
  certainty        VARCHAR(20),
  impact_area      VARCHAR(32),

  ingestion_batch  VARCHAR(10) DEFAULT 'daily',
  source_type      VARCHAR(20) NOT NULL,
  source           TEXT,
  url              TEXT,

  raw_json_sha256 CHAR(64)     NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS cd_catalyst_pub_idx
  ON core.catalyst_daily (catalyst_id, published_at DESC);
CREATE INDEX IF NOT EXISTS cd_pub_idx
  ON core.catalyst_daily (published_at DESC);
```

### Purpose
- Stores **daily extracted mentions** of catalysts from high-frequency sources.
- Used for near-real-time monitoring and incremental updates.
- Append-only table with referential link to `catalyst_master`.

### Usage
- AI agents insert mentions as they are extracted.
- Later promoted into weekly aggregation after deduplication.

---

### Purpose
- Provides a single entry point for all catalyst mentions.
- Supports unified queries across both ingestion cadences.

---

## Design Philosophy
- **Clarity over complexity:** one purpose per table.
- **AI-friendly:** categorical enums, minimal ambiguity.
- **Extensible:** `impact_area` and `magnitude_class` support multi-dimensional analysis.
- **Auditable:** `raw_json` preserves original extraction context.

---

### Example Analytical Angles
| Perspective | Fields Involved | Example Query |
|--------------|----------------|----------------|
| Catalyst Intensity | `magnitude_class`, `impact_area` | Identify top high-impact catalysts per quarter. |
| Lifecycle Tracking | `state`, `certainty_class` | Monitor catalysts moving from planned → confirmed → realized. |
| Thematic Exposure | `impact_area`, `catalyst_type` | Assess which companies are driven by regulation vs profitability. |

---

