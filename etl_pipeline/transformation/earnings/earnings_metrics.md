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
  WHEN eps IS NULL OR eps_prev IS NULL THEN 'Unknown'
  WHEN eps_prev < 0 AND eps > 0 THEN 'Turnaround'
  WHEN eps_prev > 0 AND eps < 0 THEN 'Profit to Loss'
  WHEN eps < 0 AND eps_prev < 0 AND eps > eps_prev THEN 'Loss Narrowing'
  WHEN eps < 0 AND eps_prev < 0 AND eps < eps_prev THEN 'Loss Widening'
  WHEN eps > 0 AND eps_prev > 0 AND eps > eps_prev THEN 'Positive Growth'
  WHEN eps > 0 AND eps_prev > 0 AND eps < eps_prev THEN 'Profit Decline'
  WHEN ABS(eps - eps_prev) / GREATEST(ABS(eps), ABS(eps_prev), 1e-6) <= 0.05 THEN 'Flat'
  ELSE 'Unknown'
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

### **Beat Strength Classes**

| **Range (surprise_pct)** | **Class** | **Meaning / Signal** |
|:--|:--|:--|
| ≥ **+10%** | **Major Beat** | Exceptional outperformance — significantly above expectations. |
| **+3% to +10%** | **Moderate Beat** | Clear upside surprise — strong positive signal. |
| **+1% to +3%** | **Slight Beat** | Mild outperformance — modest but positive result. |
| **−1% to +1%** | **In-Line** | Effectively met expectations — neutral, within noise tolerance. |
| **−5% to −1%** | **Slight Miss** | Small shortfall — mild underperformance. |
| ≤ **−5%** | **Major Miss** | Clear disappointment — significant underperformance. |


---


### **Regime Rules**

| **ID** | **Condition** | **Regime** | **Meaning / Signal** |
|:--|:--|:--|:--|
| B1 | `beat_count_4q ≥ 3` **and** `beat_streak_length ≥ 3` | **Consistent Outperformer** | Continuous beats with stability — elite reliability. |
| B2 | `beat_count_4q ≥ 3` **and** `beat_streak_length = 1–2` | **Frequent Beater** | Generally strong; occasional interruptions. |
| B3 | `beat_count_4q = 3` **and** `beat_streak_length = 0` | **Broken Streak** | Strong track record but most recent quarter missed — cooling momentum. |
| B4 | `beat_count_4q = 2` **and** `beat_streak_length = 2` | **Emerging Beater** | Recent back-to-back beats after mixed quarters — positive shift developing. |
| B5 | `beat_count_4q = 2` **and** `beat_streak_length ≤ 1` | **Mixed Performance** | Alternating beats and misses — unclear signal. |
| B6 | `beat_count_4q ≤ 1` **and** `beat_streak_length ≤ 1` | **Consistent Miss** | Persistent underperformance or early recovery attempt. |

