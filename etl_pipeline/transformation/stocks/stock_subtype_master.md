# 📘 Stock Subtype Master — Merged Version 5

This document consolidates all **Layer-2 (L2) subtype definitions** across major archetypes in the Stock Type Classification Framework, now updated to include the new **High Alpha** archetype and its subtypes.

---

## 🧩 1. Pre-Profit
```python
if (eps_ttm < 0) or (ocf_ttm < 0):
    classify("Pre-Profit")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Pre-Revenue / Concept Stage** | Minimal or no revenue, focused on product or technology development. | `if revenue_ttm < 5000000:` |
| 2 | **R&D-Led** | Majority of expenses in research and development. | `if r_and_d_to_revenue >= 0.5:` |
| 3 | **Scale-Up / Early Commercialization** | Revenue accelerating with high reinvestment. | `if revenue_yoy_ttm > 0.25 and reinvestment_ratio >= 0.25:` |
| 4 | **Market-Share Expansion** | Spending heavily on marketing and customer acquisition. | `if s_and_m_to_revenue >= 0.4:` |
| 5 | **Speculative / Story-Driven** | Valuation based on long-term narrative, not fundamentals. | `if narrative_intensity >= 0.6:` |

---

## 🚀 2. Hypergrowth
```python
if revenue_yoy_ttm >= 0.35:
    classify("Hypergrowth")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Efficient Hypergrowth** | Revenue growth with improving margins. | `if operating_margin_growth_ttm > 0:` |
| 2 | **Reinvestment-Heavy Hypergrowth** | Aggressive reinvestment for market share. | `if reinvestment_ratio >= 0.5:` |
| 3 | **Frontier / Technology Hypergrowth** | R&D intensity drives expansion. | `if r_and_d_to_revenue >= 0.4:` |
| 4 | **High-Margin Hypergrowth** | Sustained high gross/operating margins. | `if operating_margin_ttm > 0.25:` |
| 5 | **Platform Hypergrowth** | Multi-product or ecosystem-based expansion. | `if platform_revenue_share >= 0.4:` |

---

## 📈 3. Sustainable Growth
```python
if (revenue_yoy_ttm >= 0.10) and (eps_ttm > 0 or ocf_ttm > 0):
    classify("Sustainable Growth")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Operational Optimization** | Profitable growth with improving margins or operating leverage. | `if operating_margin_growth_ttm > 0 or ocf_yoy_ttm > 0:` |
| 2 | **Quality Compounder** | High return on equity/capital with efficient scaling. | `if roe_ttm >= 0.15 or roic_ttm >= 0.10:` |
| 3 | **Steady Performer** | Predictable margins and revenue stability. | `if revenue_vol_8q <= 0.05 and -0.01 <= operating_margin_growth_ttm <= 0.01:` |
| 4 | **Cash Flow Expansion** | Consistent YoY growth in OCF over multiple quarters. | `if ocf_yoy_ttm > 0 and ocf_yoy_streak_4q >= 3:` |

---

## ⚡ 4. Accelerating Growth
```python
if (revenue_yoy_ttm >= 0.10) and (accel_yoy_ttm > 0) and (accel_yoy_ttm_prev > 0):
    if (eps_ttm > 0 or ocf_ttm > 0):
        classify("Accelerating Growth")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Margin Acceleration** | Multi-period improvement in operating margins. | `if (operating_margin_growth_ttm > 0) and (operating_margin_growth_ttm > operating_margin_growth_ttm_1qago) and (operating_margin_growth_ttm_1qago > operating_margin_growth_ttm_2qago):` |
| 2 | **Cash Flow Acceleration** | OCF growth rate improving for at least 3 consecutive quarters. | `if (ocf_yoy_ttm > 0) and (ocf_yoy_ttm > ocf_yoy_ttm_1qago) and (ocf_yoy_ttm_1qago > ocf_yoy_ttm_2qago):` |
| 3 | **Profit Acceleration** | EPS growth improving sequentially across 3 periods. | `if (eps_yoy_ttm > 0) and (eps_yoy_ttm > eps_yoy_ttm_1qago) and (eps_yoy_ttm_1qago > eps_yoy_ttm_2qago):` |
| 4 | **Catalyst-Driven Acceleration** | Acceleration linked to identifiable catalysts (e.g. product or guidance). | `if catalyst_intensity >= 0.5:` |

---

## 💼 5. Mature / Steady
```python
if (0 <= revenue_yoy_ttm < 0.10) and (eps_ttm > 0 or ocf_ttm > 0):
    classify("Mature / Steady")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Cash Flow Stability** | Consistent positive OCF with low volatility. | `if ocf_vol_8q <= 0.05:` |
| 2 | **Margin Preservation** | Flat to slightly rising margins under low growth. | `if -0.01 <= operating_margin_growth_ttm <= 0.02:` |
| 3 | **Efficiency Maintainer** | Strong capital returns with low variance in efficiency. | `if roe_vol_8q <= 0.03 and roic_ttm >= 0.10:` |

---

## 🛡️ 6. Defensive / Low-Beta
```python
if (beta_2y <= 0.8) and (ocf_ttm > 0) and (revenue_yoy_ttm >= 0):
    classify("Defensive / Low-Beta")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Essential Consumer / Utility Defensive** | Non-discretionary demand from staples, healthcare, or utilities. | `if sector in ('Consumer Staples','Utilities','Healthcare'):` |

---

## 💰 7. Dividend / Buyback
```python
if (dividend_yield + buyback_yield) >= 0.04:
    classify("Dividend / Buyback")
```

### Definition
Companies that **return 4% or more of their market value to shareholders** annually through **dividends and/or share repurchases**.  
This archetype identifies firms that prioritize **capital return discipline** over reinvestment or expansion.

---

## 💎 8. High Alpha
```python
if (alpha_12m > 0.05) and (sharpe_ratio_12m >= 1.0):
    classify("High Alpha")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** | **Example Companies** |
|:--:|:--|:--|:--|:--|
| 1 | **Revenue Alpha** | Alpha driven by exceptional top-line growth or reacceleration vs peers. | `if revenue_yoy_ttm > (sector_avg_revenue_yoy + 0.10):` | Super Micro, Palantir, Snowflake |
| 2 | **EPS Alpha** | Alpha led by strong or accelerating earnings growth. | `if eps_yoy_ttm > 0.15 or eps_accel_4q > 0:` | Nvidia, Apple, Meta |
| 3 | **Catalyst Alpha** | Outperformance linked to identifiable catalysts such as guidance raises or new product cycles. | `if catalyst_intensity >= 0.5:` | AMD, Meta, Tesla |
| 4 | **Sentiment Alpha** | Alpha driven by narrative or investor sentiment improvement. | `if sentiment_trend_4q > 0 and eps_yoy_ttm <= 0:` | Palantir, C3.ai |
| 5 | **Momentum Alpha** | Sustained price momentum and risk-adjusted outperformance. | `if price_momentum_12m >= 0.15 and sharpe_ratio_12m >= 1.0:` | Nvidia, Tesla |
| 6 | **Recovery Alpha** | Alpha generated during early rebound after prior underperformance. | `if alpha_12m > 0 and alpha_24m < 0:` | Meta (2023), Disney (2024) |

---

## 📉 9. Decline / Distressed
```python
if (revenue_yoy_ttm < 0) and ((ocf_ttm < 0) or (operating_margin_growth_ttm < 0)):
    classify("Decline / Distressed")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Revenue Decline** | Multi-quarter contraction in revenue. | `if revenue_yoy_streak_4q < 0:` |
| 2 | **Margin Erosion** | Sequential decline in margins. | `if operating_margin_growth_ttm < 0:` |
| 3 | **Cash Burn** | Negative OCF over multiple quarters. | `if ocf_streak_4q < 0:` |
| 4 | **Debt Pressure / Overleveraged** | Leverage increasing or coverage deteriorating. | `if net_debt_to_ebitda_ttm > 4.0 or interest_coverage_ttm < 2.0:` |

---

## 🔁 10. Turnaround / Recovery
```python
if (revenue_yoy_ttm > 0) and (ocf_ttm > 0 or eps_ttm > 0) and (ocf_ttm_4qago < 0 or revenue_yoy_ttm_4qago < 0):
    classify("Turnaround / Recovery")
```

### Subtypes
| **#** | **Subtype** | **Definition** | **Logic (Simplified)** |
|:--:|:--|:--|:--|
| 1 | **Revenue Recovery** | Growth turns positive after a contraction phase. | `if revenue_yoy_ttm > 0 and revenue_yoy_ttm_4qago < 0:` |
| 2 | **Profitability Turnaround** | EPS or OCF shifts from negative to positive. | `if (eps_ttm > 0 or ocf_ttm > 0) and (eps_ttm_4qago < 0 or ocf_ttm_4qago < 0):` |
| 3 | **Margin Recovery** | Margins recovering after erosion. | `if operating_margin_growth_ttm > 0 and operating_margin_growth_ttm_4qago < 0:` |
| 4 | **Sentiment / Catalyst Re-Rating** | Market sentiment or catalysts signal structural fix. | `if sentiment_trend_4q > 0 or catalyst_intensity >= 0.5:` |

---

**© Vincent Sham — AI Agent for Stock Analysis (2025)**

