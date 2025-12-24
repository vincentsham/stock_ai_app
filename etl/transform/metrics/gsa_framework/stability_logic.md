# 2️⃣ Stability Logic

### Purpose
Evaluates the **consistency**, **predictability**, and **resilience** of performance trends over time.  
While growth measures direction and strength, **stability** measures *reliability*: whether the series behaves in a controlled, signal-dominant way or exhibits random volatility and structural disturbances.

---

## Core Metrics \& Formulas

| **Metric Type** | **Formula / Logic** | **Interpretation** |
|------------------|---------------------|--------------------|
| **Volatility (4Q or 8Q)** | `σ = STDDEV(yoy_pct over last 4–8 quarters)` | Captures noise and variability of growth. |
| **Baseline Mean** | `μ = MEAN(yoy_pct over last 4–8 quarters)` | Defines the “normal” central growth tendency. |
| **Inlier Test (1.5σ rule)** | `abs(yoy_pct_t − μ) ≤ 1.5σ` | Determines if the latest observation is within expected variation. |

---

## Interpretation Logic

### **A. Noise Layer — Volatility Regime**

| **volatility** | **Regime** | **Meaning** |
|-----------------|-------------|--------------|
| σ < 0.05 | **Low Volatility** | Predictable and controlled trend. |
| 0.05 ≤ σ < 0.10 | **Moderate Volatility** | Some variability but manageable. |
| σ ≥ 0.10 | **High Volatility** | Erratic or unstable series. |

> Use volatility as the **base condition**: low σ means the system’s structure is inherently stable.

---

### **B. Inlier Layer — Latest Behavior vs. History**

| **Condition** | **Regime** | **Meaning** |
|----------------|-------------|--------------|
| Low σ + Inlier (within ±1.5σ) | **Stable** | Predictable and typical performance. |
| Low σ + Outlier (positive direction) | **Stable but Disturbed (Positive)** | Over-performance vs. baseline; possibly temporary upside. |
| Low σ + Outlier (negative direction) | **Stable but Disturbed (Negative)** | Stable structure but negative deviation — early sign of weakness or shock. |
| High σ + Inlier | **Volatile but Calm** | Usually noisy but currently within normal range. |
| High σ + Outlier | **Volatile (Outlier)** | Both structurally and situationally unstable. |

---

### **C. Drift \& Structural Stability Layer**

| **Condition** | **Regime** | **Meaning** |
|----------------|-------------|--------------|
| μ ≥ +0.02 | **Stable Positive Drift** | Consistent and healthy baseline trend. |
| −0.02 < μ < +0.02 | **Flat Stable** | Stable but near-zero growth — acceptable maintenance phase. |
| μ ≤ −0.02 | **Structurally Deteriorating** | Trend is stable but anchored in decline — risk of deeper weakness. |

> Even if volatility is low, a persistently negative μ indicates *stable contraction* rather than health.

---

### **D. Composite Stability Evaluation**

| **Volatility (σ)** | **Inlier Flag** | **Drift (μ)** | **Regime** | **Analyst / AI Interpretation** |
|---------------------|-----------------|----------------|-------------|---------------------------------|
| Low | True | ≥ 0 | **Stable** | Reliable, predictable performance within expected range. |
| Low | False (positive outlier) | ≥ 0 | **Stable but Disturbed (+)** | Outperformance beyond normal band; may revert to mean. |
| Low | False (negative outlier) | ≥ 0 or slightly − | **Stable but Disturbed (−)** | Temporarily weak print; possible early deterioration. |
| Low | Any | μ < −0.02 | **Structurally Deteriorating** | Steady but negative base trend. |
| High | True | Any | **Volatile but Calm** | Unstable structure showing temporary balance. |
| High | False | Any | **Volatile / Unstable** | Chaotic behavior with no reliability. |

---

### **E. Interpretation Summary**

| **Regime** | **Core Meaning** | **Practical Implication** |
|-------------|------------------|----------------------------|
| **Stable** | Predictable and consistent; no action needed. | Healthy operational rhythm. |
| **Stable but Disturbed (+)** | Short-term outperformance above trend. | Watch for normalization. |
| **Stable but Disturbed (−)** | Stable system but current weakness. | Possible early breakdown. |
| **Volatile but Calm** | Normally noisy but temporarily balanced. | Limited reliability; trend may shift. |
| **Structurally Deteriorating** | Consistently low or negative baseline. | Sustained erosion — high-risk zone. |
| **Volatile / Unstable** | Irregular and unpredictable. | Poor signal quality; low confidence in forecasts. |

---

### Summary
**Stability** is a *two-layer evaluation*:
1. **Noise Layer (Volatility):** Measures predictability and reliability.  
2. **Trend Layer (Inlier + Drift):** Determines whether recent behavior is normal or disturbed, and whether the long-term mean is improving or deteriorating.

This composite logic ensures that:
- **Flat but stable** performance is acceptable,  
- **Stable but disturbed** negative prints are early warnings, and  
- **Volatility + persistent negative drift** signals structural instability.
