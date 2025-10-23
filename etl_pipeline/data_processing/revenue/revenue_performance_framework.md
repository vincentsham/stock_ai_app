# Revenue Performance Framework

### Purpose
Evaluates a company’s **top-line growth health and consistency** through three analytical dimensions — **Growth**, **Stability**, and **Acceleration** — culminating in a unified **Revenue Performance Score (0–10)**.  

This framework quantifies the strength, reliability, and momentum of revenue expansion, ensuring consistency and comparability with Profitability, Efficiency, Cash Flow, and Balance Sheet analyses.

---

## 1️⃣ Growth Logic

### Purpose
Measures how strongly **revenue** is expanding or contracting year-over-year, identifying companies with improving demand strength and market share momentum.

### Key Metrics & Formulas

| **Metric Type** | **Core Growth Formula** | **Interpretation** |
|------------------|------------------------|--------------------|
| **Revenue Growth** | `(revenue_t / revenue_{t−4}) − 1` | Measures annualized top-line expansion; reflects demand growth and competitive positioning. |

### Interpretation Logic

| **YoY Growth (%)** | **Regime** | **Meaning** |
|---------------------|------------|--------------|
| ≥ 30% | **Very strong growth** | Exceptional expansion; demand surge or market capture. |
| 10% – 30% | **Strong growth** | Sustained, healthy top-line expansion. |
| 0% – 10% | **Modest growth** | Stable but limited growth momentum. |
| −10% – 0% | **Mild contraction** | Temporary softening or normalization. |
| < −10% | **Deep contraction** | Structural decline; macro or product-specific weakness. |

---

## 2️⃣ Stability Logic

### Purpose
Evaluates how consistent revenue trends are over time — distinguishing companies with predictable top-line performance from those with volatile growth patterns.

### Key Metrics & Formulas

| **Metric Type** | **Volatility Measure** | **Stability Threshold** |
|------------------|------------------------|--------------------------|
| **Revenue Volatility (4Q)** | `STDDEV(revenue_yoy_pct, 4Q)` | Stable if < 0.05 (5 pp). |

### Interpretation Logic

| **volatility_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|--------------------|-----------------------|-------------|--------------|
| < threshold | True or False | **Stable** | Predictable revenue base with consistent growth. |
| ≥ threshold | True | **Stable (noise)** | Within tolerance band — effectively steady. |
| ≥ threshold | False | **Volatile** | Significant revenue swings or demand instability. |

---

## 3️⃣ Acceleration Logic (Stability-Aware)

### Purpose
Identifies whether revenue growth momentum is **improving**, **slowing**, or **flat**, while filtering out quarterly fluctuations and statistical noise.

### Key Metrics & Formulas

| **Metric Type** | **ΔYoY Formula** | **Noise Band Formula** |
|------------------|-----------------|--------------------------|
| **Revenue Growth Change (ΔYoY)** | `ΔYoY = revenue_yoy_pct_t − revenue_yoy_pct_{t−1}` | Measures quarter-to-quarter change in YoY growth. |
| **Noise Band (pp)** | `noise_band = max(0.003, 0.5 × revenue_volatility_4q)` | Defines tolerance range to ignore small, random movements. |

### Interpretation Logic

| **accel_vs_last_year** | **accel_count_4q** | **stable_noise_flag** | **Regime** | **Meaning** |
|-------------------------|--------------------|------------------------|-------------|--------------|
| True | ≥ 3 | False | **Strong acceleration** | Growth improving across multiple quarters. |
| True | 1–2 | False | **Post-peak deceleration** | Growth still above last year but cooling sequentially. |
| True or False | any | True | **Stable (noise)** | Movement within noise band; no meaningful shift. |
| False | any | False | **Weak / Declining** | Growth momentum weakening relative to prior periods. |

---

## 4️⃣ Revenue Composite Scoring Framework

### Purpose
Aggregates the three dimensions — **Growth**, **Stability**, and **Acceleration** — into a single **Revenue Performance Score (0–10)** for consistent cross-firm comparison.

### Subscores

| **Dimension** | **Input Metric** | **Score Scale (0–10)** | **Weight (wᵢ)** | **Insight** |
|----------------|------------------|------------------------|------------------|-------------|
| **Growth** | `revenue_yoy_pct` | `growth_score = clip((revenue_yoy_pct × 100) / 2, 0, 10)` | **0.40** | Magnitude and direction of top-line expansion. |
| **Acceleration** | `ΔYoY` | `accel_score = 10 × accel_confidence` | **0.35** | Pace of improvement and growth momentum. |
| **Stability** | `revenue_volatility_4q` | `stability_score = max(0, 10 − 200 × revenue_volatility_4q)` | **0.25** | Predictability and consistency of revenue growth. |

### Composite Formula

\[
\text{Revenue\_Score}_{0–10} = (0.40 × growth\_score) + (0.35 × accel\_score) + (0.25 × stability\_score)
\]

### Interpretation Guide

| **Score Range** | **Overall View** | **Analyst / AI Insight** |
|------------------|------------------|--------------------------|
| **8 – 10** | Excellent | Strong, accelerating, and consistent top-line growth. |
| **6 – 8** | Good | Healthy and sustainable revenue expansion. |
| **4 – 6** | Neutral | Mixed or moderate performance. |
| **2 – 4** | Weak | Decelerating or unstable revenue trends. |
| **0 – 2** | Poor | Contraction or high volatility in top-line results. |

