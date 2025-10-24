# Balance Sheet Health (Liquidity & Leverage) Performance Framework

### Purpose
Evaluates a company’s **financial resilience and solvency**, assessing how effectively it manages liquidity and leverage to sustain operations through economic cycles.  

This framework focuses on two key dimensions:

1. **Current Ratio (CR)** → *Liquidity* — ability to meet short-term obligations.  
2. **Debt-to-Equity Ratio (D/E)** → *Leverage* — balance between debt financing and shareholder equity.  

The same standardized structure — **Growth → Stability → Acceleration → Composite Score** — is applied, with **directional inversion** for leverage metrics (since *lower D/E is better*).

---

## 1️⃣ Growth Logic

### Purpose
Measures whether the company’s balance sheet strength is improving — increasing liquidity or decreasing leverage.

### Key Metrics & Formulas

| **Metric Type** | **Core Growth Formula** | **Interpretation** |
|------------------|------------------------|--------------------|
| **Current Ratio Growth** | `(cr_t / cr_{t−4}) − 1` | Positive growth = improving liquidity. |
| **Debt-to-Equity Change** | `−(de_t / de_{t−4} − 1)` | Inverted — decreasing D/E is a *positive* improvement. |

*(Note: The negative sign inverts leverage direction, so both metrics align — “higher is better.”)*

### Interpretation Logic

| **Growth (%)** | **Regime** | **Meaning** |
|----------------|------------|--------------|
| ≥ 20% | **Very strong improvement** | Major liquidity strengthening or deleveraging. |
| 5% – 20% | **Strong improvement** | Gradual improvement in balance sheet health. |
| 0% – 5% | **Stable** | Consistent financial position. |
| −10% – 0% | **Mild deterioration** | Slight weakening; still manageable. |
| < −10% | **Sharp deterioration** | Leverage rising or liquidity tightening — higher financial risk. |

---

## 2️⃣ Stability Logic

### Purpose
Assesses the *consistency* of liquidity and leverage levels over time. Stable balance sheets imply disciplined capital management.

### Key Metrics & Formulas

| **Metric Type** | **Volatility Measure** | **Stability Threshold** |
|------------------|------------------------|--------------------------|
| **Current Ratio** | `STDDEV(cr_yoy_change, 4Q)` | Stable if < 0.10 (10 pp). |
| **Debt-to-Equity** | `STDDEV(de_yoy_change, 4Q)` | Stable if < 0.12 (12 pp). |

### Interpretation Logic

| **volatility_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|--------------------|-----------------------|-------------|--------------|
| < threshold | True or False | **Stable** | Liquidity and leverage levels consistent; low refinancing risk. |
| ≥ threshold | True | **Stable (noise)** | Minor movement; within acceptable variance. |
| ≥ threshold | False | **Volatile** | Rapid shifts in debt or liquidity — potential balance sheet stress. |

---

## 3️⃣ Acceleration Logic (Stability-Aware)

### Purpose
Identifies whether balance sheet health is improving or weakening more rapidly — filtering out small fluctuations.

### Key Metrics & Formulas

| **Metric Type** | **ΔYoY Formula** | **Noise Band Formula** |
|------------------|-----------------|--------------------------|
| **Current Ratio** | `ΔYoY = cr_yoy_change_t − cr_yoy_change_{t−1}` | `noise_band = max(0.005, 0.5 × cr_volatility_4q)` |
| **Debt-to-Equity** | `ΔYoY = −(de_yoy_change_t − de_yoy_change_{t−1})` | `noise_band = max(0.006, 0.5 × de_volatility_4q)` |

### Interpretation Logic

| **accel_vs_last_year** | **accel_count_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|-------------------------|--------------------|------------------------|-------------|--------------|
| True | ≥ 3 | False | **Strong improvement** | Rapid strengthening in liquidity or deleveraging. |
| True | 1–2 | False | **Moderate improvement** | Improving but not broad-based. |
| True or False | any | True | **Stable (noise)** | Minimal change; consistent balance sheet. |
| False | any | False | **Weakening** | Deterioration in solvency — liquidity tightening or leverage rising. |

---

## 4️⃣ Balance Sheet Composite Scoring Framework

### Purpose
Combines liquidity and leverage signals into a unified **Balance Sheet Health Score (0–10)** — evaluating both short-term and long-term solvency strength.

### Subscores

| **Dimension** | **Input Metric** | **Score Scale (0–10)** | **Weight (wᵢ)** | **Insight** |
|----------------|------------------|------------------------|------------------|-------------|
| **Current Ratio (CR)** | `cr_yoy_pct` | `cr_score = clip((cr_yoy_pct × 100) / 3, 0, 10)` | **0.5** | Measures short-term solvency improvement. |
| **Debt-to-Equity (D/E)** | `−de_yoy_pct` | `de_score = clip((−de_yoy_pct × 100) / 3, 0, 10)` | **0.5** | Reflects deleveraging or financial risk reduction. |

### Composite Formula

\[
\text{BalanceSheet\_Score}_{0–10} =
(0.5 × cr\_score) +
(0.5 × de\_score)
\]

### Interpretation Guide

| **Score Range** | **Overall View** | **Analyst / AI Insight** |
|------------------|------------------|--------------------------|
| **8 – 10** | Excellent | Strong liquidity and conservative leverage; highly resilient balance sheet. |
| **6 – 8** | Good | Solid solvency; well-managed debt. |
| **4 – 6** | Neutral | Adequate but unexceptional financial position. |
| **2 – 4** | Weak | Liquidity tightening or leverage creeping higher. |
| **0 – 2** | Poor | Financial fragility; elevated debt risk or potential solvency issues. |
