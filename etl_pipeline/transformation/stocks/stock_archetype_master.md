# 📘 Stock Archetype Master — Refined Lifecycle Framework with Classification Logics

This document defines the **core Layer-1 archetypes** used in the stock type classification system, along with their **logical detection rules** for AI-based classification.

Each archetype represents a distinct **phase in the corporate lifecycle**, capturing how a company allocates capital, manages growth, and transitions between strategic regimes.

---

## 🧭 Core Archetypes (9-Phase Framework)

| **#** | **Archetype** | **Phase Keyword** | **Definition (Strategic Posture)** | **Behavioral Focus** | **Example Companies** |
|:--:|:--|:--|:--|:--|:--|
| **1** | **Speculative / Story-Driven** | *Optionality* | Early-stage or theme-driven firms valued mainly on future narratives rather than proven business models. | Narrative momentum, pre-commercial validation, investor hype. | C3.ai, QuantumScape, early clean-tech. |
| **2** | **Pre-Profit** | *Validation* | Companies building or proving product-market fit; focus on innovation and user scaling, not profits. | Heavy R&D, marketing, and fundraising. | Rivian, Unity, early biotech. |
| **3** | **Hypergrowth** | *Dominance* | Proven models scaling explosively to capture market share; reinvestment prioritized over profits. | Aggressive expansion, network effects, category leadership. | Snowflake, Datadog, Monday.com, early CrowdStrike. |
| **4** | **Sustainable Growth** | *Execution* | Profitable, efficient scaling with predictable growth and reinvestment discipline; includes breakout and quality compounders. | Operational leverage, reinvestment, capital return balance. | Palantir (2024), Robinhood (2024), Microsoft, Salesforce. |
| **5** | **Transformational Growth** | *Re-Ignition* | Mature companies reigniting growth through strategic pivots or innovation (e.g., AI, new product cycles). | R&D investment, product relaunch, platform transitions. | Meta, AMD, Netflix (ads), Microsoft (AI). |
| **6** | **Value / Reassessment** | *Recognition* | Fundamentally sound but undervalued companies being re-rated due to improving performance or sentiment. | EPS/margin recovery, multiple expansion, yield support. | Pfizer, Citi, HPQ, Alibaba. |
| **7** | **Income & Defensive** | *Preservation* | Low-growth, cash-generative firms prioritizing dividends and resilience over expansion. | Dividend stability, conservative balance sheets. | Coca-Cola, Verizon, Walmart, Procter & Gamble. |
| **8** | **Turnaround / Recovery** | *Repair* | Companies executing a structured plan to restore profitability and credibility after decline. | Margin recovery, operational resets, leadership change. | Intel, Disney, Boeing, Peloton. |
| **9** | **Crisis / Distressed** | *Survival* | Firms facing solvency or liquidity challenges, restructuring to survive. | Cost cuts, asset sales, debt renegotiation. | WeWork, Bed Bath & Beyond, Evergrande. |

---

## 🔄 Lifecycle Flow (with Turnaround Loopback)

```
          ┌───────────────────────┐
          │   Speculative / Story │
          └────────────┬──────────┘
                       ↓
                 Pre-Profit
                       ↓
                 Hypergrowth
                       ↓
              Sustainable Growth
                       ↓
            Transformational Growth
                       ↓
             Value / Reassessment
                       ↓
             Income & Defensive
                       ↓
                 Crisis / Distressed
                       ↑
                       │
              Turnaround / Recovery
                       │
                       └──────────────→ (returns to Sustainable Growth)
```

---

# 🧠 Archetype Classification Logics

Each section below defines **detection criteria**, **signals**, and **pseudocode logic** for automated archetype inference.

---

## 1. Speculative / Story-Driven

**Intent:** Valued on *potential*, not *performance.*

**Signals:**
- Minimal or volatile revenue
- Negative EPS and OCF
- Narrative-heavy transcripts (“plan”, “expect”, “pilot”, “regulatory approval”)
- High catalyst intensity, low revenue impact

**Logic:**
```python
if revenue_ttm < MIN_REVENUE or product_stage == "pre-commercial":
    if eps_ttm < 0 and ocf_ttm < 0:
        archetypes.add(("Speculative / Story-Driven", 0.85))
```

---

## 2. Pre-Profit

**Intent:** Building and validating, not yet profitable.

**Signals:**
- Recurring revenue but loss-making
- R&D or S&M very high
- Reinvestment-led expansion

**Logic:**
```python
if revenue_ttm >= MIN_REVENUE and (eps_ttm < 0 or ocf_ttm < 0):
    if growth_trend == "stable_or_up":
        archetypes.add(("Pre-Profit", 0.8))
```

---

## 3. Hypergrowth

**Intent:** Scaling at maximum speed; efficiency optional.

**Signals:**
- Sequential revenue acceleration
- High reinvestment (R&D + S&M)
- Rapid market capture
- Profitability improving but volatile

**Logic:**
```python
if growth_trend == "accelerating" and profitability_stable is False:
    if reinvestment_ratio > REINVEST_HIGH:
        archetypes.add(("Hypergrowth", 0.85))
```

---

## 4. Sustainable Growth

**Intent:** Profitable, steady growth with efficient scaling.

**Signals:**
- Positive EPS and OCF
- Stable or improving margins
- Balanced reinvestment and capital returns

**Logic:**
```python
if (eps_ttm > 0 or ocf_ttm > 0) and margin_trend in ("flat","up"):
    if not in_restructuring:
        archetypes.add(("Sustainable Growth", 0.9))
```

---

## 5. Transformational Growth

**Intent:** Mature company launching a new growth cycle.

**Signals:**
- Core business stable
- New vector (product/tech/pivot) drives acceleration
- Strategic language: “pivot”, “AI-first”, “platform shift”

**Logic:**
```python
if base_archetype == "Sustainable Growth" and new_segment_growth >> total_growth:
    if transcript_has(["pivot","AI","new product","reaccelerate"]):
        archetypes.add(("Transformational Growth", 0.75))
```

---

## 6. Value / Reassessment

**Intent:** Solid fundamentals, undervalued by market.

**Signals:**
- Low relative valuation (P/E, EV/EBITDA, P/S)
- Improving fundamentals
- Buyback/divestiture catalysts

**Logic:**
```python
if valuation_is_low and fundamentals_stable_or_improving:
    archetypes.add(("Value / Reassessment", 0.7))
```

---

## 7. Income & Defensive

**Intent:** Stable, yield-oriented, defensive posture.

**Signals:**
- Dividend policy or payout ratio high
- Low volatility
- Cash flow stability

**Logic:**
```python
if payout_policy == "dividend" and growth_is_low and earnings_vol_low:
    archetypes.add(("Income & Defensive", 0.85))
```

---

## 8. Turnaround / Recovery

**Intent:** Actively fixing execution or financial structure.

**Signals:**
- Decline → stabilization → early recovery
- Restructuring actions or new leadership
- Margin/OCF trends improving from trough

**Logic:**
```python
if performance_was_declining and now_improving and has_restructuring_actions:
    archetypes.add(("Turnaround / Recovery", 0.9))
```

---

## 9. Crisis / Distressed

**Intent:** Immediate solvency or liquidity threat.

**Signals:**
- Negative OCF + high leverage
- Low cash runway
- Debt covenant breaches / emergency financing

**Logic:**
```python
if liquidity_risk or solvency_risk:
    archetypes = [("Crisis / Distressed", 1.0)]
```

---

## ⚙️ Classification Orchestration (Node Logic)

```python
archetypes = []

check_crisis(...)
check_turnaround(...)
check_pre_profit(...)
check_hypergrowth(...)
check_sustainable(...)
check_transformational(...)
check_value(...)
check_income_defensive(...)
check_speculative(...)

archetypes = sorted(archetypes, key=lambda x: x[1], reverse=True)
return archetypes
```

**Priority Order:**
1. Crisis overrides all  
2. Turnaround requires decline + fix evidence  
3. Structural stage (Pre-Profit → Hypergrowth → Sustainable)  
4. Overlays (Transformational, Value, Income)  

---

### ✅ Framework Highlights

| **Feature** | **Benefit** |
|:--|:--|
| **Logic-first structure** | Enables consistent and explainable AI classification. |
| **Confidence weighting** | Allows multi-archetype blending by probability. |
| **Sequential evaluation** | Models corporate evolution naturally. |
| **Practical signals** | Combines metrics + transcripts + catalysts. |
| **Complete coverage** | Works across all market sectors and stages. |

---

### © Vincent Sham — Stock AI Agent Project (2025)
