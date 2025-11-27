# Aggregate the table `raw.analyst_price_targets` and `raw.analyst_grades` for monthly statistics

## 🧩 Purpose
A **30-day rolling aggregation** of analyst activity and stock performance per ticker, summarizing:

- **Analyst grades** (Buy/Hold/Sell distributions and rating changes)  
- **Price targets (PT)** (consensus levels and PT direction changes)  
- **Analyst-implied returns** (`PT / price_when_posted − 1`) and revisions vs. prior notes  
- **Stock price statistics** over the same 30-day window  

The table provides a compact yet comprehensive snapshot of analyst sentiment, expectations, and real-world market context.

---

## 🧭 Structure Overview

```jsonc
{
  "tic": "AAPL",
  "start_date": "2025-09-15",
  "end_date": "2025-10-15",
  "grade_stats": { ... },
  "grade_actions": { ... },
  "pt_stats": { ... },
  "pt_actions": { ... },
  "return_stats": { ... },
  "return_actions": { ... },
  "price_stats": { ... }
}
```

---

## 🧱 Field Definitions

### **Root**
| Field | Type | Description |
|--------|------|-------------|
| `tic` | TEXT | Stock ticker symbol |
| `start_date` | DATE | Start date of the 30-day aggregation window |
| `end_date` | DATE | End date of the 30-day aggregation window |

---

### **grade_stats**
> Distribution of analyst ratings (Buy/Hold/Sell) during the 30-day window.

| Field | Type | Description |
|--------|------|-------------|
| `count` | INTEGER | Total number of rating actions |
| `buy_n` | INTEGER | Count of Buy or Overweight ratings |
| `hold_n` | INTEGER | Count of Hold or Neutral ratings |
| `sell_n` | INTEGER | Count of Sell or Underweight ratings |
| `buy_ratio` | NUMERIC | `buy_n / count` |
| `hold_ratio` | NUMERIC | `hold_n / count` |
| `sell_ratio` | NUMERIC | `sell_n / count` |
| `grade_balance` | NUMERIC | `(buy_n − sell_n) / count` — sentiment proxy (+1 = all buys, −1 = all sells) |

---

### **grade_actions**
> Rating direction changes relative to previous analyst notes.

| Field | Type | Description |
|--------|------|-------------|
| `upgrade_n` | INTEGER | Number of rating upgrades (e.g., Hold → Buy) |
| `downgrade_n` | INTEGER | Number of rating downgrades (e.g., Buy → Hold) |
| `init_n` | INTEGER | Number of initiations (new coverage) |
| `reiterate_n` | INTEGER | Number of reiterated ratings (no change) |

---

### **pt_stats**
> Summary statistics of analysts’ price targets within the 30-day window.

| Field | Type | Description |
|--------|------|-------------|
| `count` | INTEGER | Number of PTs issued |
| `high` | NUMERIC | Highest PT |
| `low` | NUMERIC | Lowest PT |
| `p25` | NUMERIC | 25th percentile PT |
| `median` | NUMERIC | Median PT |
| `p75` | NUMERIC | 75th percentile PT |
| `mean` | NUMERIC | Arithmetic mean PT |
| `stddev` | NUMERIC | Standard deviation of PTs |
| `dispersion` | NUMERIC | `p75 − p25` (fallback: `high − low`) |

---

### **pt_actions**
> PT directional movements across the 30-day window.

| Field | Type | Description |
|--------|------|-------------|
| `upgrade_n` | INTEGER | Number of PT increases |
| `downgrade_n` | INTEGER | Number of PT decreases |
| `reiterate_n` | INTEGER | Number of unchanged PTs |
| `init_n` | INTEGER | Number of new PTs from coverage initiation |

---

### **return_stats**
> Analyst-implied return metrics (`PT / price_when_posted − 1`).

| Field | Type | Description |
|--------|------|-------------|
| `mean` | NUMERIC | Mean implied return |
| `median` | NUMERIC | Median implied return |
| `p25` | NUMERIC | 25th percentile implied return |
| `p75` | NUMERIC | 75th percentile implied return |
| `stddev` | NUMERIC | Standard deviation of implied returns |
| `dispersion` | NUMERIC | `p75 − p25` (fallback: `high − low`) |
| `high` | NUMERIC | Maximum implied return (most bullish) |
| `low` | NUMERIC | Minimum implied return (most bearish) |

---

### **return_actions**
> Directional changes in implied return vs. previous analyst note (`prev_price_when_posted`).  
> Thresholds for upgrade/downgrade are **volatility-adjusted** based on the stock’s  
> `price_stats.stddev` (price volatility) over the same 30-day period.

| Field | Type | Description |
|--------|------|-------------|
| `upgrade_n` | INTEGER | Analysts whose implied return increased more than one `price_stats.stddev` |
| `downgrade_n` | INTEGER | Analysts whose implied return decreased more than one `price_stats.stddev` |
| `reiterate_n` | INTEGER | Analysts whose implied return changed within ±`price_stats.stddev` |
| `init_n` | INTEGER | Analysts initiating new coverage (no prior record) |

---

### **price_stats**
> Stock price distribution over the same 30-day period.

| Field | Type | Description |
|--------|------|-------------|
| `start` | NUMERIC | Price at the beginning of the window |
| `end` | NUMERIC | Price at the end of the window |
| `high` | NUMERIC | Highest closing price during the window |
| `low` | NUMERIC | Lowest closing price during the window |
| `p25` | NUMERIC | 25th percentile price |
| `median` | NUMERIC | Median price |
| `p75` | NUMERIC | 75th percentile price |
| `mean` | NUMERIC | Arithmetic mean price |
| `stddev` | NUMERIC | Standard deviation of daily prices (used as dynamic threshold for `return_actions`) |

---

## 🧠 Example JSON Record

```json
{
  "tic": "DLO",
  "start_date": "2025-09-15",
  "end_date": "2025-10-15",
  "grade_stats": {
    "count": 3,
    "buy_n": 2,
    "hold_n": 1,
    "sell_n": 0,
    "buy_ratio": 0.67,
    "hold_ratio": 0.33,
    "sell_ratio": 0.0,
    "grade_balance": 0.67
  },
  "grade_actions": {
    "upgrade_n": 1,
    "downgrade_n": 0,
    "init_n": 0,
    "reiterate_n": 1
  },
  "pt_stats": {
    "count": 12,
    "high": 12.5,
    "low": 10.2,
    "p25": 10.8,
    "median": 11.2,
    "p75": 11.6,
    "mean": 11.3,
    "stddev": 0.42,
    "dispersion": 0.8
  },
  "pt_actions": {
    "upgrade_n": 3,
    "downgrade_n": 1,
    "reiterate_n": 6,
    "init_n": 2
  },
  "return_stats": {
    "mean": 0.09,
    "median": 0.08,
    "p25": 0.05,
    "p75": 0.12,
    "stddev": 0.04,
    "dispersion": 0.07,
    "high": 0.18,
    "low": -0.03
  },
  "return_actions": {
    "upgrade_n": 4,
    "downgrade_n": 2,
    "reiterate_n": 5,
    "init_n": 1
  },
  "price_stats": {
    "start": 9.8,
    "end": 10.4,
    "high": 10.7,
    "low": 9.6,
    "p25": 9.8,
    "median": 10.2,
    "p75": 10.5,
    "mean": 10.1,
    "stddev": 0.28
  }
}
```
