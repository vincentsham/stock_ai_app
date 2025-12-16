
# Signalist v1 – Metric Direction & Percentile Rules

This document defines **v1 rules** for each metric in Signalist:
1. Whether **higher values are always better** (direction)
2. Whether a **percentile bar should be shown** in the UI

Global assumptions for v1:
- Percentiles are **global (no peer groups yet)**
- UI percentiles are always normalized so **higher = better**
- Low-is-better metrics are **internally inverted**
- Color bands: **0–33 red / 34–66 yellow / 67–100 green**

---

## Valuation

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| market_cap | No | No | Size metric |
| pe_ttm | No | Yes | Invert |
| pe_forward | No | Yes | Invert |
| ev_to_ebitda_ttm | No | Yes | Invert |
| fcf_yield_ttm | Yes | Yes | Core valuation signal |
| ps_ttm | No | Yes | Invert |
| ev_to_revenue_ttm | No | Yes | Invert |
| p_to_fcf_ttm | No | Yes | Invert |
| peg_ratio | No | Yes | Invert |
| price_to_book | No | Yes | Invert |
| ev_to_fcf_ttm | No | Yes | Invert |
| earnings_yield_ttm | Yes | Yes | Yield metric |
| revenue_yield_ttm | Yes | Yes | Yield metric |

---

## Profitability

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| gross_margin | Yes | Yes | |
| operating_margin | Yes | Yes | |
| ebitda_margin | Yes | Yes | |
| net_margin | Yes | Yes | |
| roe | Yes | Yes | |
| roa | Yes | Yes | |
| ocf_margin | Yes | Yes | |
| fcf_margin | Yes | Yes | |

---

## Growth

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| revenue_growth_yoy | Yes | Yes | |
| revenue_cagr_3y | Yes | Yes | |
| eps_growth_yoy | Yes | Yes | Volatile |
| eps_cagr_3y | Yes | Yes | |
| fcf_growth_yoy | Yes | Yes | |
| fcf_cagr_3y | Yes | Yes | |
| revenue_cagr_5y | Yes | Yes | |
| eps_cagr_5y | Yes | Yes | |
| fcf_cagr_5y | Yes | Yes | |
| ebitda_growth_yoy | Yes | Yes | |
| operating_income_growth_yoy | Yes | Yes | |
| forward_revenue_growth | Yes | Yes | |
| forward_eps_growth | Yes | Yes | |

---

## Efficiency

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| asset_turnover | Yes | Yes | |
| cash_conversion_cycle | No | Yes | Invert |
| dso | No | Yes | Invert |
| dio | No | Yes | Invert |
| dpo | Mostly | Optional | Context dependent |
| fixed_asset_turnover | Yes | Yes | |
| revenue_per_employee | Yes | Yes | Industry-biased |
| opex_ratio | No | Yes | Invert |

---

## Financial Health

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| net_debt | No | No | Absolute size |
| net_debt_to_ebitda_ttm | No | Yes | Invert |
| interest_coverage_ttm | Yes | Yes | |
| current_ratio | Yes | Yes | |
| quick_ratio | Yes | Yes | |
| cash_ratio | Yes | Yes | |
| debt_to_equity | No | Yes | Invert |
| debt_to_assets | No | Yes | Invert |
| fixed_charge_coverage_ttm | Yes | Yes | |
| altman_z_score | Yes | Yes | Non-financials |
| cash_runway_months | Yes | Yes | Loss-makers |

---

## Capital Allocation

| Metric | Higher Better? | Show Percentile | Notes |
|------|---------------|-----------------|-------|
| roic | Yes | Yes | Core Signalist metric |
| total_shareholder_yield | Yes | Yes | Dividends + buybacks |
| share_count_change_yoy | No | Yes | Invert (buybacks good) |
| reinvestment_rate | Depends | Optional | Needs ROIC context |
| fcf_per_share_growth_yoy | Yes | Yes | Strong long-term signal |

---

## v1 Summary Rules

- UI always displays **higher percentile = better**
- Low-is-better metrics are **internally inverted**
- Percentile bars are shown only where **better vs worse is meaningful**
- Size metrics (e.g. market cap, absolute debt) **do not get percentile bars**
