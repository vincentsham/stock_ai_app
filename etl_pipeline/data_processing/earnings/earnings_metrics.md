# 📊 Earnings Metrics

## 🧩 Overview

This document defines all **derived metrics** used for evaluating corporate earnings performance based on  
**EPS**, **estimated EPS**, **revenue**, and **estimated revenue**.

It covers:
- Surprise & beat detection  
- Growth, acceleration, and consistency metrics  
- EPS phase classification (turnaround, loss-narrowing, profit-decline, etc.)  
- Momentum tracking across short, medium, and long horizons  

All formulas are conceptual and can be implemented in **SQL**, **Python**, or within the **ETL layer**.

---

## ⚙️ Core Calculation Principles

### 1. Relative Change (for stability)
To measure small movements fairly across magnitudes:
$$
rel\_change = \frac{|x_t - x_{t-1}|}{\max(|x_t|, |x_{t-1}|, 1e^{-6})}
$$

---

### 2. Flat / Neutral Rule
If `rel_change ≤ 0.05` (5% tolerance), classify as **flat_or_neutral**.  
This suppresses noise and avoids false “growth” signals.

---

### 3. Sign-Safe Growth

> Used for **QoQ**, **YoY**, and **TTM** comparisons.

```sql
CASE
  WHEN x_prev IS NULL THEN NULL
  WHEN x_prev = 0 THEN NULL
  WHEN x_prev < 0 AND x > 0 THEN  2.0     -- turnaround (+200%)
  WHEN x_prev > 0 AND x < 0 THEN -1.0     -- positive → negative (−100%)
  WHEN ABS(x - x_prev) / GREATEST(ABS(x), ABS(x_prev), 1e-6) <= 0.05 THEN 0.0
  ELSE LEAST(GREATEST((x - x_prev) / ABS(x_prev), -2.0), 2.0)
END
```

**Growth flag:**
```sql
(growth > 0)::int
```

---

### 4. Sign-Safe Surprise %

> Measures deviation from analyst estimates or consensus expectations.

```sql
CASE
  WHEN x_est IS NULL THEN NULL
  WHEN x_est = 0 THEN NULL
  WHEN ABS(x - x_est) / GREATEST(ABS(x_est), 1e-6) <= 0.05 THEN 0.0
  ELSE LEAST(GREATEST((x - x_est) / ABS(x_est), -2.0), 2.0)
END
```

**Beat flag:**
```sql
(surprise > 0)::int
```

---

### 5. EPS Phase Classification
Describes direction and sign transition of EPS.

```sql
CASE
  WHEN eps IS NULL OR eps_prev IS NULL THEN 'unknown'
  WHEN eps_prev < 0 AND eps > 0 THEN 'turnaround'
  WHEN eps_prev > 0 AND eps < 0 THEN 'profit_to_loss'
  WHEN eps < 0 AND eps_prev < 0 AND eps > eps_prev THEN 'loss_narrowing'
  WHEN eps < 0 AND eps_prev < 0 AND eps < eps_prev THEN 'loss_widening'
  WHEN eps > 0 AND eps_prev > 0 AND eps > eps_prev THEN 'positive_growth'
  WHEN eps > 0 AND eps_prev > 0 AND eps < eps_prev THEN 'profit_decline'
  WHEN ABS(eps - eps_prev) / GREATEST(ABS(eps), ABS(eps_prev), 1e-6) <= 0.05 THEN 'flat_or_neutral'
  ELSE 'unknown'
END
```

---

## 📘 Metric Reference Table

### 🧾 Surprise & Beat Metrics
| Metric | Description | Formula | Horizon |
|:--|:--|:--|:--|
| `{prefix}_surprise_pct` | Surprise vs estimates (sign-safe) | Safe surprise formula | Short-term |
| `{prefix}_beat_flag` | 1 if surprise > 0 | `(surprise_pct > 0)::int` | Short-term |
| `{prefix}_beat_count_4q` | Count of beats over last 4 quarters | `SUM(beat_flag) OVER 4Q` | Medium-term |
| `{prefix}_beat_streak_length` | Consecutive beat streak | `COUNT consecutive 1s` | Medium-term |
| `{prefix}_consistency` | Surprise volatility | `STDDEV(surprise_pct) OVER 4Q` | Long-term |

---

### 📈 Growth Metrics
| Metric | Description | Formula | Horizon |
|:--|:--|:--|:--|
| `{prefix}_qoq_growth_pct` | QoQ growth (sign-safe) | `(x_t - x_t−1) / |x_t−1|` | Short-term |
| `{prefix}_growth_flag` | 1 if QoQ growth > 0 | `(qoq_growth_pct > 0)::int` | Short-term |
| `{prefix}_growth_count_4q` | Number of positive QoQ growths (4Q) | `SUM(growth_flag) OVER 4Q` | Medium-term |
| `{prefix}_growth_streak_length` | Current streak of positive growth | `COUNT consecutive growth_flag = 1` | Medium-term |
| `{prefix}_yoy_growth_pct` | YoY growth (vs. t−4) | Safe growth formula | Medium-term |
| `{prefix}_trend_strength` | Mean YoY growth (smoothness) | `AVG(yoy_growth_pct) OVER 4Q` | Long-term |
| `{prefix}_consistency` | Volatility of YoY growth | `STDDEV(yoy_growth_pct) OVER 4Q` | Long-term |
| `{prefix}_ttm_growth_pct` | Trailing-12M growth | `(TTM_t − TTM_t−4) / |TTM_t−4|` | Long-term |

---

### ⚡ Acceleration Metrics
| Metric | Description | Formula | Horizon |
|:--|:--|:--|:--|
| `{prefix}_acceleration` | Change in YoY growth | `Δ(yoy_growth_pct)` | Medium-term |
| `{prefix}_ttm_acceleration` | Change in TTM growth | `Δ(ttm_growth_pct)` | Long-term |
| `{prefix}_acceleration_flag` | 1 if growth improving | `(acceleration > 0)::int` | Medium-term |
| `{prefix}_acceleration_count_4q` | Number of positive accelerations (4Q) | `SUM(acceleration_flag) OVER 4Q` | Medium-term |
| `{prefix}_acceleration_streak_length` | Consecutive quarters of acceleration | `COUNT consecutive acceleration_flag = 1` | Long-term |

---

### 💰 EPS Phase Metrics
| Metric | Description | Formula / Rule | Horizon |
|:--|:--|:--|:--|
| `eps_phase` | EPS trend classification | EPS phase CASE logic | Short-term |

---

## 🧠 Summary by Category

| Category | Purpose |
|:--|:--|
| **Surprise & Beat Metrics** | Capture near-term performance vs expectations |
| **Growth Metrics** | Measure operational momentum |
| **Acceleration Metrics** | Identify turning points and regime changes |
| **Consistency Metrics** | Quantify volatility and predictability |
| **Trend & TTM Metrics** | Evaluate sustained direction over multiple quarters |
| **EPS Phase** | Provide qualitative interpretation of earnings trajectory |

---

## ✅ Design Rationale
- **Sign-safe logic** handles negative or small denominators robustly  
- **±200% cap** prevents extreme ratios from distorting analysis  
- **5% tolerance** filters noise and minor deltas  
- **Rolling 4Q windows** unify frequency treatment  
- **Acceleration flags** isolate early signs of trend improvement  
- **Categorical + quantitative metrics** integrate seamlessly into AI agent or scoring systems  
- **Symmetric EPS/Revenue structure** allows uniform comparisons across profitability and sales dimensions  
