# 📘 Stock Archetype Master

This document defines the **Layer-1 (L1) archetypes** used in the stock type classification system, updated to reflect the refined Version 16 framework. It follows the structure of the original Archetype Master document while incorporating the simplified logic and lifecycle consistency of the new system.

---

## 🧭 1. Purpose
Stock archetypes establish the **foundational classification** for how companies should be analyzed, benchmarked, and scored.  
They represent the **core financial and behavioral identities** of companies within your multi-agent AI stock analysis system.

Each archetype determines which performance dimensions—growth, stability, or cyclicality—should be emphasized in the scoring model.  
Together, they form the backbone of the **Growth – Stability – Acceleration** framework and guide both peer comparison and lifecycle tracking.

---

## 🔄 2. Lifecycle Flow (Updated)
```
Pre-Profit → Hypergrowth → Sustainable Growth → Accelerating Growth
       ↓
Mature / Steady → Defensive / Low-Beta → Cyclical
       ↓
Decline / Distressed → Turnaround / Recovery → Sustainable Growth
```
This flow represents a company’s typical financial evolution—from early-stage risk to sustained maturity, through downturns and back into recovery.

---

## 🧱 3. Core Archetype Reference Table

| **#** | **Archetype** | **Definition (Strategic Posture)** | **Primary Signals** | **Example Companies** |
|:--:|:--|:--|:--|:--|
| **1** | **Pre-Profit** | Early-stage companies still loss-making but scaling rapidly. | `eps_ttm < 0` or `ocf_ttm < 0` | Rivian, Unity, early Snowflake |
| **2** | **Hypergrowth** | Companies expanding explosively, prioritizing market share over profit. | `revenue_yoy_ttm ≥ 0.35` | Snowflake, Datadog, Shopify (2020–2021) |
| **3** | **Sustainable Growth** | Profitable firms maintaining efficient double-digit growth. | `revenue_yoy_ttm ≥ 0.10` and `(eps_ttm > 0 or ocf_ttm > 0)` | Microsoft, Salesforce, Apple (2023–2024) |
| **4** | **Accelerating Growth** | Growth rate itself is improving; momentum is rising. | `(revenue_yoy_ttm ≥ 0.10)` and `(accel_yoy_ttm > 0 and accel_yoy_ttm_prev > 0)` | Palantir (2024), NVIDIA (2023–24), Meta (2023) |
| **5** | **Mature / Steady** | Stable, profitable phase with modest growth; efficient and predictable. | `(0 ≤ revenue_yoy_ttm < 0.10)` and `(eps_ttm > 0 or ocf_ttm > 0)` | Apple (2024), PepsiCo, Visa, McDonald’s, Cisco |
| **6** | **Defensive / Low-Beta** | Cash-positive, low-volatility companies with steady performance. | `(beta_2y ≤ 0.8)` and `(ocf_ttm > 0)` and `(revenue_yoy_ttm ≥ 0)` | Procter & Gamble, Coca-Cola, J&J, Walmart |
| **7** | **Cyclical** | Businesses with repeated up-down demand and margin cycles. | `count_sign_changes(revenue_yoy_8q) ≥ 2` or `count_sign_changes(operating_margin_growth_8q) ≥ 2` | Caterpillar, ExxonMobil, Delta, Micron, Ford |
| **8** | **Decline / Distressed** | Firms facing structural deterioration or financial stress. | `(revenue_yoy_ttm < 0)` and `((ocf_ttm < 0) or (operating_margin_growth_ttm < 0))` | IBM, 3M, Peloton, WeWork |
| **9** | **Turnaround / Recovery** | Returning to growth and profitability after decline. | `(revenue_yoy_ttm > 0)` and `(ocf_ttm > 0 or eps_ttm > 0)` and `(ocf_ttm_4qago < 0 or revenue_yoy_ttm_4qago < 0)` | Intel (2024), Disney (2024), Boeing (2024) |

---

## ⚙️ 4. Archetype Logic Overview
Each archetype is detected through a combination of **quantitative signals** (revenue, EPS, OCF, margins, beta) and **trend patterns** (acceleration, sign changes).  
Below are the simplified detection forms derived from Version 16.

```python
# Pre-Profit
if (eps_ttm < 0) or (ocf_ttm < 0):
    classify("Pre-Profit")

# Hypergrowth
if (revenue_yoy_ttm >= 0.35):
    classify("Hypergrowth")

# Sustainable Growth
if (revenue_yoy_ttm >= 0.10) and (eps_ttm > 0 or ocf_ttm > 0):
    classify("Sustainable Growth")

# Accelerating Growth
if (revenue_yoy_ttm >= 0.10) and (accel_yoy_ttm > 0) and (accel_yoy_ttm_prev > 0):
    if (eps_ttm > 0 or ocf_ttm > 0):
        classify("Accelerating Growth")

# Mature / Steady
if (0 <= revenue_yoy_ttm < 0.10) and (eps_ttm > 0 or ocf_ttm > 0):
    classify("Mature / Steady")

# Defensive / Low-Beta
if (beta_2y <= 0.8) and (ocf_ttm > 0) and (revenue_yoy_ttm >= 0):
    classify("Defensive / Low-Beta")

# Cyclical
if (count_sign_changes(revenue_yoy_8q) >= 2) or (count_sign_changes(operating_margin_growth_8q) >= 2):
    classify("Cyclical")

# Decline / Distressed
if (revenue_yoy_ttm < 0) and ((ocf_ttm < 0) or (operating_margin_growth_ttm < 0)):
    classify("Decline / Distressed")

# Turnaround / Recovery
if (revenue_yoy_ttm > 0) and (ocf_ttm > 0 or eps_ttm > 0) and (ocf_ttm_4qago < 0 or revenue_yoy_ttm_4qago < 0):
    classify("Turnaround / Recovery")
```

---

## 📊 5. Lifecycle Usage Notes
* Archetypes define **financial regime context** — they determine which metrics (growth, margin, volatility) the model should emphasize.
* Companies may hold **multiple overlapping archetypes** temporarily (e.g., *Accelerating Growth + Cyclical*).
* Archetypes evolve sequentially but reversals are common; the full transition chain provides interpretability for lifecycle analysis.
* L2 subtypes and L3 tags extend interpretability but are documented separately.

---

## 🧩 6. Example Lifecycle Transitions
| Company | Transition Pattern |
|:--|:--|
| **Palantir** | Pre-Profit → Sustainable Growth → Accelerating Growth |
| **Apple** | Sustainable Growth → Mature / Steady → Defensive / Low-Beta |
| **NVIDIA** | Sustainable Growth → Accelerating Growth → Cyclical |
| **Intel** | Decline / Distressed → Turnaround / Recovery → Sustainable Growth |

---

**© Vincent Sham — AI Agent for Stock Analysis (2025)**

