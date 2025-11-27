# 1️⃣ Growth Logic

### Purpose
Quantifies the **absolute strength**, **direction**, and **persistence** of performance change relative to the same quarter in the prior year.  
Captures both the **magnitude** of growth and its **consistency** across recent quarters.

---

## Core Metrics & Formulas

| **Metric Type** | **Formula / Logic** | **Interpretation** |
|------------------|---------------------|--------------------|
| **YoY Growth (%)** | `(value_t / value_{t−4}) − 1` | Measures annualized change adjusted for seasonality. |
| **Growth Count (4Q)** | `Σ [yoy_pct_{t−i} > 0] for i = 0..3` | Counts how many of the past 4 quarters showed positive YoY growth. |
| **Growth Streak Length** | Count of consecutive quarters ending in *t* where `sign(yoy_pct_i)` = `sign(yoy_pct_t)` | Measures the length of the current directional run (growth or contraction). |

---

## Interpretation Logic

### **A. YoY Growth Regime**

| **YoY Growth (%)** | **Regime** | **Meaning** |
|---------------------|------------|--------------|
| ≥ 30% | **Very Strong Growth** | Exceptional expansion; major positive inflection. |
| 10% – 30% | **Strong Growth** | Sustained and healthy improvement. |
| 0% – 10% | **Modest Growth** | Mild expansion; neutral performance. |
| −10% – 0% | **Mild Contraction** | Temporary decline or normalization. |
| < −10% | **Deep Contraction** | Structural deterioration or severe slowdown. |

---

### **B. Growth Count (Last 4 Quarters)**

| **growth_count_4q** | **Regime** | **Meaning** |
|----------------------|-------------|--------------|
| 4 | **Sustained Expansion** | Continuous YoY growth across all recent quarters. |
| 3 | **Mostly Expanding** | Growth in most quarters; minor slowdown or one-off dip. |
| 2 | **Mixed Phase** | Half growing, half contracting — unclear trend. |
| 1 | **Mostly Contracting** | Weak performance with limited rebound signals. |
| 0 | **Persistent Contraction** | Continuous YoY decline — deep deterioration. |

---

### **C. Growth Streak Length**

| **growth_streak_len** | **Regime** | **Meaning** |
|------------------------|-------------|--------------|
| ≥ 4 | **Extended Uptrend** | Multi-quarter sustained growth cycle. |
| 2–3 | **Developing Uptrend** | Strengthening but still early in cycle. |
| 1 | **New Inflection** | Just turned positive or negative — early trend reversal. |
| 0 | **Flat / Alternating** | No clear direction or alternating growth signs. |

> For negative streaks (continuous contraction), apply the same interpretation in reverse.

---

## Combined Growth Evaluation

### Inputs
- **YoY%** = `(value_t / value_{t−4}) − 1`
- **growth_count_4q** = `Σ [yoy_pct_{t−i} > 0]` for `i=0..3`  (0–4)
- **growth_streak_len** = consecutive quarters (ending at *t*) with same sign as `yoy_pct_t` (cap at 6 for labeling)

### Regime Rules (apply in order)
1. **Persistent Contraction**  
   If `YoY% < 0` **and** `growth_count_4q ≤ 1` **and** `growth_streak_len ≥ 3`.
2. **Sustained Growth**  
   If `YoY% ≥ 10%` **and** `growth_count_4q = 4` **and** `growth_streak_len ≥ 3`.
3. **Emerging Recovery**  
   If `YoY% > 0` **and** `growth_count_4q = 3` **and** `growth_streak_len = 1–2`.
4. **Tentative Turnaround**  
   If `YoY% < 0` **and** `growth_count_4q = 2–3` **and** `growth_streak_len = 1`.
5. **Volatile Transition**  
   If `growth_count_4q = 2` **and** `growth_streak_len ≤ 2` (mixed/alternating signs).
6. **Neutral / Plateau**  
   Otherwise (near-zero YoY or conflicting signals).

### Regime Rules

| **ID** | **Condition** | **Regime** | **Meaning / Signal** |
|:--|:--|:--|:--|
| R1 | `growth_count_4q = 4` **and** `growth_streak_len ≥ 3` | **Sustained Expansion** | Broad-based, durable growth across all recent quarters. |
| R2 | `growth_count_4q ≥ 3` **and** `growth_streak_len = 1–2` | **Developing Expansion** | Growth mostly positive but recently reset; early-cycle phase. |
| R3 | `growth_count_4q = 2` **and** `growth_streak_len ≤ 2` | **Volatile Transition** | Mixed pattern — expansion alternating with contraction. |
| R4 | `growth_count_4q ≤ 1` **and** `growth_streak_len ≤ 1` | **Tentative Turnaround** | Only one recent growth quarter; weak or fragile signal. |
| R5 | `growth_count_4q = 0` **and** `growth_streak_len = 0` | **Persistent Contraction** | No positive momentum at all — deep down-cycle. |


---

### Summary
The **Growth Logic** now combines:
1. **Magnitude** — how strong growth is (`yoy_pct`)
2. **Persistence** — how often growth has been positive (`growth_count_4q`)
3. **Continuity** — how long the trend has lasted (`growth_streak_len`)

Together, these form a robust foundation for measuring **structural strength** and **durability of expansion** before evaluating Stability or Acceleration.

