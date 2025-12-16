# Efficiency (Return Metrics) Performance Framework

### Purpose
Measures how effectively a company converts its **assets, equity, and invested capital** into profit.  
This framework evaluates **return efficiency** through three key ratios:

1. **ROE (Return on Equity)** → *Shareholder efficiency* — profitability relative to equity base.  
2. **ROA (Return on Assets)** → *Asset utilization* — how efficiently assets generate profit.  
3. **ROIC (Return on Invested Capital)** → *Capital productivity* — overall return from both debt and equity capital.

Each applies the same structure — **Growth → Stability → Acceleration → Composite Score** — ensuring consistency with your existing financial pillars.

---

## 1️⃣ Growth Logic

### Purpose
Quantifies how return metrics (ROE, ROA, ROIC) are improving or declining relative to prior periods.

### Key Metrics & Formulas

| **Metric Type** | **Core Growth Formula** | **Interpretation** |
|------------------|------------------------|--------------------|
| **ROE Growth** | `(roe_t / roe_{t−4}) − 1` | Measures YoY improvement in shareholder profitability. |
| **ROA Growth** | `(roa_t / roa_{t−4}) − 1` | Indicates asset utilization improvement. |
| **ROIC Growth** | `(roic_t / roic_{t−4}) − 1` | Reflects operational capital efficiency change. |

### Interpretation Logic

| **YoY Growth (%)** | **Regime** | **Meaning** |
|---------------------|------------|--------------|
| ≥ 20% | **Very strong growth** | Substantial improvement in capital returns. |
| 5% – 20% | **Strong growth** | Meaningful expansion of efficiency metrics. |
| 0% – 5% | **Modest growth** | Steady, incremental improvement. |
| −5% – 0% | **Mild decline** | Slight deterioration; normal fluctuation. |
| < −5% | **Sharp decline** | Structural erosion of return efficiency. |

---

## 2️⃣ Stability Logic

### Purpose
Assesses how consistent efficiency ratios remain over time, distinguishing reliable operators from volatile performers.

### Key Metrics & Formulas

| **Metric Type** | **Volatility Measure** | **Stability Threshold** |
|------------------|------------------------|--------------------------|
| **ROE** | `STDDEV(roe, 4Q)` | Stable if < 0.02 (2 pp). |
| **ROA** | `STDDEV(roa, 4Q)` | Stable if < 0.015 (1.5 pp). |
| **ROIC** | `STDDEV(roic, 4Q)` | Stable if < 0.02 (2 pp). |

### Interpretation Logic

| **volatility_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|--------------------|-----------------------|-------------|--------------|
| < threshold | True or False | **Stable** | Return efficiency is predictable and reliable. |
| ≥ threshold | True | **Stable (noise)** | Small quarter-to-quarter movement, still consistent. |
| ≥ threshold | False | **Volatile** | Efficiency ratios fluctuate significantly — unreliable performance. |

---

## 3️⃣ Acceleration Logic (Stability-Aware)

### Purpose
Detects inflection points in capital efficiency trends — identifying whether returns are improving, plateauing, or deteriorating.

### Key Metrics & Formulas

| **Metric Type** | **ΔYoY Formula** | **Noise Band Formula** |
|------------------|-----------------|--------------------------|
| **ROE** | `ΔYoY = roe_yoy_pct_t − roe_yoy_pct_{t−1}` | `noise_band = max(0.002, 0.5 × roe_volatility_4q)` |
| **ROA** | `ΔYoY = roa_yoy_pct_t − roa_yoy_pct_{t−1}` | `noise_band = max(0.0015, 0.5 × roa_volatility_4q)` |
| **ROIC** | `ΔYoY = roic_yoy_pct_t − roic_yoy_pct_{t−1}` | `noise_band = max(0.002, 0.5 × roic_volatility_4q)` |

### Interpretation Logic

| **accel_vs_last_year** | **accel_count_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|-------------------------|--------------------|------------------------|-------------|--------------|
| True | ≥ 3 | False | **Strong acceleration** | Sustained expansion in return efficiency. |
| True | 1–2 | False | **Post-peak deceleration** | Returns still positive but slowing. |
| True or False | any | True | **Stable (noise)** | Marginal fluctuation; no directional change. |
| False | any | False | **Weak / Declining** | Efficiency ratios deteriorating across periods. |

---

## 4️⃣ Efficiency Composite Scoring Framework

### Purpose
Aggregates ROE, ROA, and ROIC trends into a single numeric **Efficiency Score (0–10)** to summarize how effectively capital generates profits.

### Subscores

| **Dimension** | **Input Metric** | **Score Scale (0–10)** | **Weight (wᵢ)** | **Insight** |
|----------------|------------------|------------------------|------------------|-------------|
| **ROE** | `roe_yoy_pct` | `roe_score = clip((roe_yoy_pct × 100) / 4, 0, 10)` | **0.4** | Shareholder-level return strength. |
| **ROA** | `roa_yoy_pct` | `roa_score = clip((roa_yoy_pct × 100) / 3, 0, 10)` | **0.3** | Asset-level utilization and efficiency. |
| **ROIC** | `roic_yoy_pct` | `roic_score = clip((roic_yoy_pct × 100) / 3, 0, 10)` | **0.3** | Capital deployment efficiency and cost of capital spread. |

### Composite Formula

\[
\text{Efficiency\_Score}_{0–10} =
(0.4 × roe\_score) +
(0.3 × roa\_score) +
(0.3 × roic\_score)
\]

### Interpretation Guide

| **Score Range** | **Overall View** | **Analyst / AI Insight** |
|------------------|------------------|--------------------------|
| **8 – 10** | Excellent | Highly efficient at converting capital into profit; strong operational discipline. |
| **6 – 8** | Good | Efficient performance with minor volatility. |
| **4 – 6** | Neutral | Average capital productivity; stable but unremarkable. |
| **2 – 4** | Weak | Deteriorating efficiency; operational drag on returns. |
| **0 – 2** | Poor | Structural decline in capital effectiveness; red flag for profitability sustainability. |
