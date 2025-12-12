# 📘 Income Statement Analysis Framework

This framework defines six dimensions of income statement analysis — from revenue growth to shareholder efficiency — designed for both human and AI-based financial interpretation.  
Each section contains metrics, formulas, key analytical questions, interpretation logic, and example output flags.

---

## 1️⃣ Revenue Performance

### Purpose
Evaluates top-line growth, stability, and quality of revenue to determine business momentum and demand consistency.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `revenue` | Measures total sales — absolute business scale. | Direct from income statement. | • What is the size of sales this quarter?<br>• Above or below trend? | `revenue_level_flag`: `"High" / "Normal" / "Low"` |
| `revenue_yoy_pct` | Tracks long-term growth momentum. | `(CurrentRevenue - PriorYearRevenue) / PriorYearRevenue` | • Is revenue expanding YoY?<br>• How fast vs peers? | `revenue_growth_flag` → `True` if > 0.<br>`strong_revenue_growth_flag` → `True` if > 5%. |
| `revenue_qoq_pct` *(optional)* | Sequential momentum. | `(CurrentRevenue - PriorQuarterRevenue) / PriorQuarterRevenue` | • Is revenue accelerating sequentially?<br>• Seasonal strength? | `revenue_acceleration_flag` → `True` if `qoq > 0` and `yoy > prior_yoy`. |
| `revenue_volatility_4q` | Stability of revenue growth. | `STDDEV(revenue_yoy_pct over last 4 quarters)` | • Are sales predictable or volatile? | `revenue_stability_flag` → `True` if volatility < 5%. |
| `revenue_growth_vs_market_growth` | Benchmarks growth vs peers. | `revenue_yoy_pct - market_revenue_yoy_pct` | • Is the company outperforming the market? | `outperform_flag` → `True` if > +2 pp. |
| `recurring_revenue_ratio` *(optional)* | Quality of sales. | `RecurringRevenue / TotalRevenue` | • How durable is revenue base? | `revenue_quality_flag`: `"High" / "Moderate" / "Low"` |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `revenue_yoy_pct > 0` & `volatility < 5%` | Strong, steady top-line growth. |
| `revenue_yoy_pct < 0` & stable volatility | Mature or cyclical demand. |
| `outperform_flag = True` | Market share gain or superior execution. |
| `recurring_revenue_ratio ↑` | Improving quality of sales. |

#### Example Flag Output
```json
{
  "revenue_level_flag": "Normal",
  "revenue_growth_flag": true,
  "strong_revenue_growth_flag": true,
  "revenue_acceleration_flag": false,
  "revenue_stability_flag": true,
  "outperform_flag": true,
  "revenue_quality_flag": "High"
}
```

---

## 2️⃣ Cost Structure & Gross Profitability

### Purpose
Assesses production efficiency, pricing power, and margin trends to determine cost control and profitability sustainability.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `gross_margin_pct` | Core profitability after production costs. | `grossProfit / revenue` | • Are margins healthy?<br>• Improving or deteriorating? | `gross_margin_trend_flag`: `"Expanding" / "Stable" / "Contracting"` |
| `gross_margin_change_yoy/qoq` | Trend direction. | `current_gm_pct - prior_gm_pct` | • Is margin expansion sustained? | `margin_expansion_flag` → `True` if > +0.5 pp. |
| `gross_margin_volatility_4q` | Margin stability. | `STDDEV(gross_margin_pct over 4q)` | • Are margins predictable? | `margin_stability_flag` → `True` if volatility < 1 pp. |
| `revenue_growth_vs_cogs_growth` | Cost efficiency indicator. | `revenue_yoy_pct - cogs_yoy_pct` | • Are costs rising faster than revenue? | `cost_pressure_flag` → `True` if COGS ↑ faster. |
| `gross_profit_yoy_pct` *(optional)* | Profit pool growth. | `(CurrentGP - PriorGP) / PriorGP` | • Is gross profit growing even if margin flat? | `profit_pool_growth_flag` → `True` if > 0. |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `gross_margin_pct ↑` | Improved efficiency and pricing. |
| `gross_margin_pct ↓` & `COGS ↑` | Margin compression from cost pressure. |
| `volatility < 1 pp` | Stable cost control. |
| `profit_pool_growth_flag = True` | Expanding gross profit pool. |

#### Example Flag Output
```json
{
  "gross_margin_trend_flag": "Expanding",
  "margin_expansion_flag": true,
  "margin_stability_flag": true,
  "cost_pressure_flag": false,
  "profit_pool_growth_flag": true
}
```

---

## 3️⃣ Operating Efficiency

### Purpose
Evaluates how well the company controls R&D and SG&A spending — key drivers of scalability and discipline.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `operating_expenses_ratio` | Expense intensity. | `operatingExpenses / revenue` | • Is opex scaling with sales?<br>• Improving or worsening? | `opex_efficiency_flag` → `True` if ↓ YoY. |
| `r_and_d_ratio` | Innovation investment. | `R&D / revenue` | • Is R&D investment sustainable?<br>• Supporting growth? | `r_and_d_investment_flag` → `True` if ↑ & margins stable. |
| `sgna_ratio` | Administrative efficiency. | `SG&A / revenue` | • Are overhead costs in control? | `sgna_discipline_flag` → `True` if ↓ YoY. |
| `opex_change_yoy/qoq` | Expense trend. | `current_opex_ratio - prior_opex_ratio` | • Is cost burden easing? | `opex_improvement_flag` → `True` if < 0. |
| `opex_volatility_4q` | Expense stability. | `STDDEV(opex_ratio over 4q)` | • Are costs predictable? | `opex_stability_flag` → `True` if volatility < 0.5 pp. |
| `operating_leverage_ratio` *(optional)* | Scalability. | `ΔOperatingIncome% / ΔRevenue%` | • Is profit growing faster than revenue? | `positive_leverage_flag` → `True` if > 1. |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `opex_ratio ↓` | Better cost control and scale. |
| `r_and_d_ratio ↑` + stable margins | Healthy reinvestment. |
| `sgna_ratio ↑` | Potential inefficiency or inflation impact. |
| `positive_leverage_flag = True` | Profits scaling faster than revenue. |

#### Example Flag Output
```json
{
  "opex_efficiency_flag": true,
  "r_and_d_investment_flag": true,
  "sgna_discipline_flag": true,
  "opex_improvement_flag": true,
  "opex_stability_flag": true,
  "positive_leverage_flag": true
}
```

---

## 4️⃣ Operating Profitability

### Purpose
Assesses how efficiently the company converts gross profit into operating income, signaling operational strength and scalability.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `operating_margin_pct` | Core operational profit level. | `operatingIncome / revenue` | • How profitable is the core business? | `operating_margin_trend_flag`: `"Expanding" / "Stable" / "Contracting"` |
| `operating_margin_change_yoy/qoq` | Margin trend. | `current_om_pct - prior_om_pct` | • Is margin improving? | `margin_expansion_flag` → `True` if > +0.5 pp. |
| `operating_margin_volatility_4q` | Stability of profitability. | `STDDEV(om_pct over 4q)` | • Are profits stable? | `margin_stability_flag` → `True` if volatility < 1 pp. |
| `operating_leverage_ratio` | Scalability of profits. | `ΔOperatingIncome% / ΔRevenue%` | • Does profit grow faster than sales? | `positive_leverage_flag` → `True` if > 1. |
| `ebitda_margin_pct` *(optional)* | Cash-based profit. | `EBITDA / revenue` | • How strong are cash profits? | `high_cash_margin_flag` → `True` if > 30%. |
| `ebitda_to_ebit_ratio` *(optional)* | Capital intensity. | `EBITDA / EBIT` | • Are non-cash costs significant? | `asset_light_flag` → `True` if < 1.1. |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `operating_margin_pct ↑` | Improving efficiency. |
| `operating_leverage_ratio > 1` | Positive scaling. |
| `volatility < 1 pp` | Stable operations. |
| `ebitda_to_ebit_ratio ↑` | Rising capital intensity. |

#### Example Flag Output
```json
{
  "operating_margin_trend_flag": "Expanding",
  "margin_expansion_flag": true,
  "margin_stability_flag": true,
  "positive_leverage_flag": true,
  "high_cash_margin_flag": true,
  "asset_light_flag": true
}
```

---

## 5️⃣ Earnings Performance & Quality

### Purpose
Analyzes net income, EPS, and sustainability of earnings — the ultimate measure of profitability and consistency.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `net_margin_pct` | Net profit after all expenses. | `netIncome / revenue` | • Are bottom-line profits rising? | `net_margin_trend_flag`: `"Expanding" / "Stable" / "Contracting"` |
| `eps` | Per-share earnings. | `netIncome / weightedAverageShsOutDil` | • How much profit per share?<br>• Aligned with total profit? | `eps_growth_flag` → `True` if ↑ YoY. |
| `eps_yoy_pct` | EPS growth rate. | `(CurrentEPS - PriorEPS) / PriorEPS` | • Is growth accelerating? | `eps_growth_strength_flag`: `"Strong" / "Moderate" / "Weak"` |
| `eps_volatility_4q` | Stability of profits. | `STDDEV(EPS over 4q)` | • Predictability of earnings? | `eps_stability_flag` → `True` if volatility < 5%. |
| `effective_tax_rate` | Tax efficiency. | `incomeTaxExpense / incomeBeforeTax` | • Is tax rate stable? | `tax_efficiency_flag` → `True` if < 20%. |
| `non_operating_ratio` | Non-core impact. | `totalOtherIncomeExpensesNet / EBIT` | • Are earnings clean or distorted? | `clean_earnings_flag` → `True` if |ratio| < 5%. |
| `earnings_quality_flag` *(optional)* | Composite quality indicator. | Combines volatility + non-operating ratio. | • Are earnings recurring and sustainable? | `"High" / "Moderate" / "Low"` |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `net_margin ↑` & `eps ↑` | Strengthening profitability. |
| `eps_yoy_pct > net_income_yoy_pct` | Buyback-boosted EPS. |
| `eps_volatility_4q < 5%` | Stable, high-quality earnings. |
| `non_operating_ratio > 10%` | One-time distortions. |

#### Example Flag Output
```json
{
  "net_margin_trend_flag": "Expanding",
  "eps_growth_flag": true,
  "eps_growth_strength_flag": "Strong",
  "eps_stability_flag": true,
  "tax_efficiency_flag": true,
  "clean_earnings_flag": true,
  "earnings_quality_flag": "High"
}
```

---

## 6️⃣ Capital & Shareholder Efficiency

### Purpose
Measures per-share value creation through buybacks, dilution, and dividend policy — how profits translate into shareholder returns.

| **Metric** | **Purpose** | **Formula** | **Analyst / AI Questions** | **Diagnostic Flags** |
|-------------|-------------|-------------|-----------------------------|----------------------|
| `share_change_pct` | Dilution or buybacks. | `(CurrentShares - PriorShares) / PriorShares` | • Is share count shrinking? | `buyback_flag` → `True` if < 0. |
| `eps_vs_net_income_growth_gap` | EPS leverage vs total profit. | `eps_yoy_pct - net_income_yoy_pct` | • EPS growth boosted by buybacks? | `buyback_accretion_flag` → `True` if > +2 pp. |
| `share_count_volatility_4q` | Share base stability. | `STDDEV(weightedAverageShsOutDil over 4q)` | • Frequent issuance or stable base? | `share_base_stability_flag` → `True` if < 1%. |
| `dividend_payout_ratio` *(optional)* | Profit returned to shareholders. | `Dividends / NetIncome` | • Is payout sustainable? | `high_payout_flag` → `True` if > 50%. |
| `retained_earnings_ratio` *(optional)* | Reinvestment capacity. | `(NetIncome - Dividends) / NetIncome` | • Reinvesting for growth? | `reinvestment_flag` → `True` if > 50%. |
| `shareholder_return_efficiency` *(composite)* | Combined efficiency signal. | Weighted score from buyback + payout. | • Overall capital effectiveness? | `"High" / "Moderate" / "Low"` |

#### Interpretation Logic
| **Scenario** | **Analyst / AI Insight** |
|---------------|--------------------------|
| `share_change_pct < 0` | Buybacks enhancing EPS. |
| `eps_vs_net_income_growth_gap > 0` | EPS growing faster than profit — buyback-driven. |
| `dividend_payout_ratio 20–40%` | Balanced return policy. |
| `retained_earnings_ratio > 50%` | Healthy reinvestment. |

#### Example Flag Output
```json
{
  "buyback_flag": true,
  "buyback_accretion_flag": true,
  "share_base_stability_flag": true,
  "high_payout_flag": false,
  "reinvestment_flag": true,
  "shareholder_return_efficiency": "High"
}
```

---

## 🔁 Analytical Flow Overview

```
Revenue Performance
   ↓
Cost Structure & Gross Profitability
   ↓
Operating Efficiency
   ↓
Operating Profitability
   ↓
Earnings Performance & Quality
   ↓
Capital & Shareholder Efficiency
```

Each layer represents where profitability is **created**, **retained**, or **returned** along the financial chain.
