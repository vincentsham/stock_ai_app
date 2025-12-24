# Acceleration Logic (Extended)

### Purpose
Determines whether **growth momentum** is improving, slowing, or stabilizing, while accounting for natural variability and noise. The extended version introduces **streak detection** to measure how long acceleration or deceleration trends persist, distinguishing **temporary noise** from **sustained momentum shifts**.

---

## Key Metrics & Formulas

| **Metric Type** | **Formula / Logic** | **Interpretation** |
|------------------|--------------------|--------------------|
| **ΔYoY (pp)** | `ΔYoY = yoy_pct_t − yoy_pct_{t−1}` | Sequential change in YoY growth rate (in percentage points). |
| **Acceleration Count (4Q)** | `Σ (yoy_pct_t > yoy_pct_{t−i}) for i=1..4` | Counts how many of the last 4 quarters showed improvement vs. their previous quarter — a measure of **momentum persistence**. |
| **Acceleration Streak Length** | `streak_len = count_consecutive_sign(ΔYoY)` | Number of continuous quarters with the same ΔYoY direction (positive or negative). |

> Example:  
> If ΔYoY = [+2pp, +1pp, +0.5pp, −0.8pp], then `streak_len = 3` (three consecutive accelerating quarters before turning down).

---

## Interpretation Logic

| **Regime** | **Condition** | **Interpretation** |
|-------------|----------------|--------------------|
| **Sustained Acceleration** | `accel_count_4q ≥ 3` and `streak_len ≥ 2` | Broad and continuous positive momentum — trend accelerating strongly. |
| **Choppy Acceleration** | `accel_count_4q ≥ 3` and `streak_len < 2` | Momentum breadth strong but continuity weak — likely noisy or just peaked. |
| **Emerging Acceleration** | `accel_count_4q = 2` and `streak_len = 2` | Early, forming trend — two consecutive quarters of improvement. |
| **Tentative / Mixed** | `accel_count_4q = 2` and `streak_len ≤ 1` | Improvement exists but inconsistent — unstable signal. |
| **Deceleration** | `accel_count_4q ≤ 1` | Growth momentum fading or reversing. |

---

## Suggested Scoring Extension

| **Subscore Component** | **Logic** | **Scale (0–10)** |
|--------------------------|-----------|------------------|
| `accel_score_base` | Based on sign and magnitude of ΔYoY | 0–10 |
| `accel_streak_bonus` | `+1` per additional consecutive positive streak (max +3)` | 0–3 |
| **Final accel_score** | `min(10, accel_score_base + accel_streak_bonus)` | 0–10 |

> This weighting rewards sustained improvements more than one-off spikes, aligning acceleration with **trend durability**.

---

## Analytical View

| **Scenario** | **Signal Summary** | **Insight** |
|---------------|--------------------|--------------|
| **Rising streak ≥ 3** | Sustained positive ΔYoY | Growth momentum firmly strengthening. |
| **Breaking streak** | ΔYoY flips sign | Potential turning point — watch next quarter. |
| **Flat streak (ΔYoY ≈ 0)** | Low variability | Momentum plateauing; stabilization phase. |
| **Negative streak ≥ 3** | Sustained slowdown | Likely post-peak phase or macro-driven drag. |

