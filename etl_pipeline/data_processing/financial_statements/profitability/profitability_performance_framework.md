# Profitability Performance Framework

### Purpose
Evaluates a company’s **profitability health and efficiency** through four layers of performance:

1. **Gross Profit** → *Top-line strength* — pricing power and cost discipline.  
2. **EBIT (Operating Income)** → *Operating efficiency* — how effectively core operations generate profit.  
3. **EPS (Earnings Per Share)** → *Shareholder profitability* — profit normalized per share.  
4. **Profit Margin (Net Margin %)** → *Profit quality* — efficiency and sustainability of earnings.

Each layer applies the same analytical framework — **Growth → Stability → Acceleration → Composite Score** — to ensure consistency and comparability across profitability dimensions.

---

## 1️⃣ Growth Logic

### Purpose
Measures how strongly each profitability metric is expanding or contracting YoY, identifying companies with improving earnings power across multiple levels.

### Key Metrics & Formulas

| **Metric Type** | **Core Growth Formula** | **Interpretation** |
|------------------|------------------------|--------------------|
| **Gross Profit Growth** | `(gross_profit_t / gross_profit_{t−4}) − 1` | Indicates pricing power and cost efficiency improvement. |
| **EBIT Growth** | `(ebit_t / ebit_{t−4}) − 1` | Measures core operating profit expansion; reflects leverage on revenue. |
| **EPS Growth** | `(eps_t / eps_{t−4}) − 1` | Tracks earnings expansion per share — investor return potential. |
| **Profit Margin Change** | `net_margin_pct_t − net_margin_pct_{t−4}` | Assesses profitability quality improvement per revenue dollar. |

### Interpretation Logic

| **YoY Growth (%)** | **Regime** | **Meaning** |
|---------------------|------------|--------------|
| ≥ 30% | **Very strong growth** | Exceptional profitability surge; high leverage or turnaround phase. |
| 10% – 30% | **Strong growth** | Sustained expansion and operational success. |
| 0% – 10% | **Modest growth** | Stable, low-volatility improvement. |
| −10% – 0% | **Mild contraction** | Temporary slowdown or normalization. |
| < −10% | **Deep contraction** | Structural deterioration in profitability. |

---

## 2️⃣ Stability Logic

### Purpose
Evaluates how consistent profitability trends are over time — distinguishing stable profit generators from volatile performers.

### Key Metrics & Formulas

| **Metric Type** | **Volatility Measure** | **Stability Threshold** |
|------------------|------------------------|--------------------------|
| **Gross Profit** | `STDDEV(gross_profit_yoy_pct, 4Q)` | Stable if < 0.05 (5 pp). |
| **EBIT** | `STDDEV(ebit_yoy_pct, 4Q)` | Stable if < 0.08 (8 pp). |
| **EPS** | `STDDEV(eps_yoy_pct, 4Q)` | Stable if < 0.10 (10 pp). |
| **Profit Margin** | `STDDEV(net_margin_pct, 4Q)` | Stable if < 0.03 (3 pp). |

### Interpretation Logic

| **volatility_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|--------------------|-----------------------|-------------|--------------|
| < threshold | True or False | **Stable** | Predictable profitability with low volatility. |
| ≥ threshold | True | **Stable (noise)** | Within tolerance band — effectively steady. |
| ≥ threshold | False | **Volatile** | Significant profit swings or inconsistent margins. |

---

## 3️⃣ Acceleration Logic (Stability-Aware)

### Purpose
Identifies whether profit growth momentum is **improving**, **slowing**, or **flat**, while filtering out quarter-to-quarter noise.

### Key Metrics & Formulas

| **Metric Type** | **ΔYoY Formula** | **Noise Band Formula** |
|------------------|-----------------|--------------------------|
| **Gross Profit** | `ΔYoY = gross_profit_yoy_pct_t − gross_profit_yoy_pct_{t−1}` | `noise_band = max(0.003, 0.5 × volatility_4q)` |
| **EBIT** | `ΔYoY = ebit_yoy_pct_t − ebit_yoy_pct_{t−1}` | `noise_band = max(0.004, 0.5 × volatility_4q)` |
| **EPS** | `ΔYoY = eps_yoy_pct_t − eps_yoy_pct_{t−1}` | `noise_band = max(0.005, 0.5 × volatility_4q)` |
| **Profit Margin** | `ΔYoY = net_margin_pct_t − net_margin_pct_{t−1}` | `noise_band = max(0.002, 0.5 × volatility_4q)` |

### Interpretation Logic

| **accel_vs_last_year** | **accel_count_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|-------------------------|--------------------|------------------------|-------------|--------------|
| True | ≥ 3 | False | **Strong acceleration** | Profit growth improving across multiple quarters. |
| True | 1–2 | False | **Post-peak deceleration** | Growth still positive but slowing. |
| True or False | any | True | **Stable (noise)** | Movement within tolerance; no meaningful shift. |
| False | any | False | **Weak / Declining** | Profit momentum weakening vs prior year. |

---

## 4️⃣ Profitability Composite Scoring Framework

### Purpose
Aggregates the four profitability sub-dimensions into a single numeric score (0–10) for AI-agent comparability across time and peers.

### Subscores

| **Dimension** | **Input Metric** | **Score Scale (0–10)** | **Weight (wᵢ)** | **Insight** |
|----------------|------------------|------------------------|------------------|-------------|
| **Gross Profit** | `gross_profit_yoy_pct` | `growth_score = clip((gross_profit_yoy_pct × 100) / 2, 0, 10)` | **0.25** | Reflects top-line cost efficiency. |
| **EBIT** | `ebit_yoy_pct` | `operating_score = clip((ebit_yoy_pct × 100) / 3, 0, 10)` | **0.30** | Captures core operating strength. |
| **EPS** | `eps_yoy_pct` | `eps_score = clip((eps_yoy_pct × 100) / 4, 0, 10)` | **0.25** | Measures shareholder profitability. |
| **Profit Margin** | `net_margin_change_pp` | `margin_score = clip((net_margin_change_pp × 200), 0, 10)` | **0.20** | Evaluates profitability quality and sustainability. |

### Composite Formula

\[
\text{Profitability\_Score}_{0–10} =
(0.25 × growth\_score) +
(0.30 × operating\_score) +
(0.25 × eps\_score) +
(0.20 × margin\_score)
\]

### Interpretation Guide

| **Score Range** | **Overall View** | **Analyst / AI Insight** |
|------------------|------------------|--------------------------|
| **8 – 10** | Excellent | Strong multi-layer profitability — efficient, accelerating, and stable. |
| **6 – 8** | Good | Solid operating and earnings performance with mild fluctuations. |
| **4 – 6** | Neutral | Balanced but unspectacular; profits flat or stabilizing. |
| **2 – 4** | Weak | Deteriorating or inconsistent profitability. |
| **0 – 2** | Poor | Structural decline or severe margin compression. |
