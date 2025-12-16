
# Signalist v1 – Metric Direction & Percentile Rules

This document defines **v1 interpretation rules** for each metric in Signalist:

- **Higher is better?** → shown directly  
- **Lower is better?** → internally inverted, still shown as “higher percentile = better”  
- **Notes** → context, exclusions, or caveats  

## Global Assumptions (v1)

- Percentiles are **global** (no peer groups yet)
- UI percentiles are always normalized so **higher = better**
- **Lower-is-better metrics are internally inverted**
- **Discrete color bands only**:
  - 0–33 → **Red**
  - 34–66 → **Yellow**
  - 67–100 → **Green**

---

## Valuation

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| market_cap | ❌ | ❌ | Size metric, no quality judgment |
| pe_ttm | ❌ | ✅ | Lower multiple = cheaper |
| pe_forward | ❌ | ✅ | Lower multiple = cheaper |
| ev_to_ebitda_ttm | ❌ | ✅ | Lower multiple = cheaper |
| fcf_yield_ttm | ✅ | ❌ | Core valuation signal |
| ps_ttm | ❌ | ✅ | Lower multiple = cheaper |
| ev_to_revenue_ttm | ❌ | ✅ | Lower multiple = cheaper |
| p_to_fcf_ttm | ❌ | ✅ | Lower multiple = cheaper |
| peg_ratio | ❌ | ✅ | Lower PEG preferred |
| price_to_book | ❌ | ✅ | Context-dependent |
| ev_to_fcf_ttm | ❌ | ✅ | Lower multiple = cheaper |
| earnings_yield_ttm | ✅ | ❌ | Yield metric |
| revenue_yield_ttm | ✅ | ❌ | Yield metric |

---

## Profitability

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| gross_margin | ✅ | ❌ | |
| operating_margin | ✅ | ❌ | |
| ebitda_margin | ✅ | ❌ | |
| net_margin | ✅ | ❌ | |
| roe | ✅ | ❌ | |
| roa | ✅ | ❌ | |
| ocf_margin | ✅ | ❌ | |
| fcf_margin | ✅ | ❌ | |

---

## Growth

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| revenue_growth_yoy | ✅ | ❌ | |
| revenue_cagr_3y | ✅ | ❌ | |
| eps_growth_yoy | ✅ | ❌ | Volatile |
| eps_cagr_3y | ✅ | ❌ | |
| fcf_growth_yoy | ✅ | ❌ | |
| fcf_cagr_3y | ✅ | ❌ | |
| revenue_cagr_5y | ✅ | ❌ | |
| eps_cagr_5y | ✅ | ❌ | |
| fcf_cagr_5y | ✅ | ❌ | |
| ebitda_growth_yoy | ✅ | ❌ | Optional |
| operating_income_growth_yoy | ✅ | ❌ | |
| forward_revenue_growth | ✅ | ❌ | Expectations |
| forward_eps_growth | ✅ | ❌ | Expectations |

---

## Efficiency

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| asset_turnover | ✅ | ❌ | |
| cash_conversion_cycle | ❌ | ✅ | Shorter cycle preferred |
| dso | ❌ | ✅ | Faster collections |
| dio | ❌ | ✅ | Faster inventory turnover |
| dpo | ⚠️ | ⚠️ | Context-dependent |
| fixed_asset_turnover | ✅ | ❌ | |
| revenue_per_employee | ✅ | ❌ | Industry-biased |
| opex_ratio | ❌ | ✅ | Leaner cost structure |

---

## Financial Health

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| net_debt | ❌ | ❌ | Absolute size, no percentile |
| net_debt_to_ebitda_ttm | ❌ | ✅ | Lower leverage preferred |
| interest_coverage_ttm | ✅ | ❌ | |
| current_ratio | ✅ | ❌ | |
| quick_ratio | ✅ | ❌ | |
| cash_ratio | ✅ | ❌ | |
| debt_to_equity | ❌ | ✅ | Lower leverage |
| debt_to_assets | ❌ | ✅ | Lower leverage |
| fixed_charge_coverage_ttm | ✅ | ❌ | |
| altman_z_score | ✅ | ❌ | Non-financials |
| cash_runway_months | ✅ | ❌ | Loss-makers only |

---

## Capital Allocation

| Metric | Higher is Better | Lower is Better | Notes |
|------|-----------------|-----------------|-------|
| roic | ✅ | ❌ | Core Signalist metric |
| total_shareholder_yield | ✅ | ❌ | Dividends + buybacks |
| share_count_change_yoy | ❌ | ✅ | Buybacks preferred |
| reinvestment_rate | ⚠️ | ⚠️ | Depends on ROIC |
| fcf_per_share_growth_yoy | ✅ | ❌ | Strong long-term signal |

---

## v1 Summary Rules

- **Discrete colors only** (no gradients)
- UI always shows **higher percentile = better**
- Lower-is-better metrics are **internally inverted**
- Percentiles express **signal buckets**, not fine precision
- Size-only metrics **do not imply quality**
