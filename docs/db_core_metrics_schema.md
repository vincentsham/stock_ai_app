# Database Schema Documentation

## Schema: core
**Description**: Stores calculated metrics, summaries, and scores derived from core data for analysis and UI display.

### Tables in `core` (Metrics & Summaries)
- `earnings_metrics`: Calculated metrics related to earnings events (surprises, beats).
- `analyst_rating_monthly_summary`: Monthly aggregated analyst ratings and price targets.
- `analyst_rating_quarterly_summary`: Quarterly aggregated analyst ratings and price targets.
- `analyst_rating_yearly_summary`: Yearly aggregated analyst ratings and price targets.
- `revenue_metrics`: Calculated revenue growth and trend metrics.
- `eps_diluted_metrics`: Calculated diluted EPS growth and trend metrics.
- `valuation_metrics`: Valuation ratios and metrics (PE, EV/EBITDA, etc.).
- `profitability_metrics`: Profitability margins and returns (ROE, ROA, etc.).
- `growth_metrics`: Growth rates (YoY, CAGR) for key financial line items.
- `efficiency_metrics`: Operational efficiency ratios (turnover, conversion cycles).
- `financial_health_metrics`: Balance sheet health and solvency metrics.
- `valuation_percentiles`: Percentile rankings for valuation metrics.
- `profitability_percentiles`: Percentile rankings for profitability metrics.
- `growth_percentiles`: Percentile rankings for growth metrics.
- `efficiency_percentiles`: Percentile rankings for efficiency metrics.
- `financial_health_percentiles`: Percentile rankings for financial health metrics.
- `stock_scores`: Composite scores for various financial categories.


## Table: core.earnings_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier for the metrics record |
| event_id        | UUID                       | NO          |             | Reference to the earnings event          |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | INT                        | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| eps             | FLOAT                      | YES         |             | Earnings Per Share                       |
| eps_estimated   | FLOAT                      | YES         |             | Estimated EPS                            |
| revenue         | FLOAT                      | YES         |             | Revenue                                  |
| revenue_estimated| FLOAT                     | YES         |             | Estimated Revenue                        |
| eps_regime      | VARCHAR(50)                | YES         |             | EPS Regime Classification                |
| eps_surprise    | FLOAT                      | YES         |             | EPS Surprise Value                       |
| eps_beat_flag   | SMALLINT                   | YES         |             | Flag indicating EPS beat                 |
| eps_beat_count_4q| SMALLINT                  | YES         |             | Count of EPS beats in last 4 quarters    |
| eps_beat_streak_length| SMALLINT             | YES         |             | Length of consecutive EPS beat streak    |
| eps_surprise_class| VARCHAR(50)              | YES         |             | Classification of EPS surprise           |
| eps_surprise_regime| VARCHAR(50)             | YES         |             | Regime of EPS surprise                   |
| revenue_surprise| FLOAT                      | YES         |             | Revenue Surprise Value                   |
| revenue_beat_flag| SMALLINT                  | YES         |             | Flag indicating Revenue beat             |
| revenue_beat_count_4q| SMALLINT              | YES         |             | Count of Revenue beats in last 4 quarters|
| revenue_beat_streak_length| SMALLINT         | YES         |             | Length of consecutive Revenue beat streak|
| revenue_surprise_class| VARCHAR(50)          | YES         |             | Classification of Revenue surprise       |
| revenue_surprise_regime| VARCHAR(50)         | YES         |             | Regime of Revenue surprise               |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of source data               |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.analyst_rating_monthly_summary
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| start_date      | DATE                       | NO          |             | Start date of summary period             |
| end_date        | DATE                       | NO          |             | End date of summary period               |
| pt_count        | INTEGER                    | YES         |             | Count of price targets                   |
| pt_high         | FLOAT                      | YES         |             | Highest price target                     |
| pt_low          | FLOAT                      | YES         |             | Lowest price target                      |
| pt_p25          | FLOAT                      | YES         |             | 25th percentile price target             |
| pt_median       | FLOAT                      | YES         |             | Median price target                      |
| pt_p75          | FLOAT                      | YES         |             | 75th percentile price target             |
| pt_mean         | FLOAT                      | YES         |             | Mean price target                        |
| pt_stddev       | FLOAT                      | YES         |             | Standard deviation of price targets      |
| pt_dispersion   | FLOAT                      | YES         |             | Dispersion of price targets              |
| pt_upgrade_n    | INTEGER                    | YES         |             | Number of upgrades (PT)                  |
| pt_downgrade_n  | INTEGER                    | YES         |             | Number of downgrades (PT)                |
| pt_reiterate_n  | INTEGER                    | YES         |             | Number of reiterations (PT)              |
| pt_init_n       | INTEGER                    | YES         |             | Number of initiations (PT)               |
| grade_count     | INTEGER                    | YES         |             | Count of grades                          |
| grade_buy_n     | INTEGER                    | YES         |             | Number of Buy grades                     |
| grade_hold_n    | INTEGER                    | YES         |             | Number of Hold grades                    |
| grade_sell_n    | INTEGER                    | YES         |             | Number of Sell grades                    |
| grade_buy_ratio | FLOAT                      | YES         |             | Ratio of Buy grades                      |
| grade_hold_ratio| FLOAT                      | YES         |             | Ratio of Hold grades                     |
| grade_sell_ratio| FLOAT                      | YES         |             | Ratio of Sell grades                     |
| grade_balance   | FLOAT                      | YES         |             | Balance score of grades                  |
| grade_upgrade_n | INTEGER                    | YES         |             | Number of grade upgrades                 |
| grade_downgrade_n| INTEGER                   | YES         |             | Number of grade downgrades               |
| grade_reiterate_n| INTEGER                   | YES         |             | Number of grade reiterations             |
| grade_init_n    | INTEGER                    | YES         |             | Number of grade initiations              |
| ret_mean        | FLOAT                      | YES         |             | Mean implied return                      |
| ret_median      | FLOAT                      | YES         |             | Median implied return                    |
| ret_p25         | FLOAT                      | YES         |             | 25th percentile implied return           |
| ret_p75         | FLOAT                      | YES         |             | 75th percentile implied return           |
| ret_stddev      | FLOAT                      | YES         |             | Std dev of implied return                |
| ret_dispersion  | FLOAT                      | YES         |             | Dispersion of implied return             |
| ret_high        | FLOAT                      | YES         |             | Highest implied return                   |
| ret_low         | FLOAT                      | YES         |             | Lowest implied return                    |
| price_start     | FLOAT                      | YES         |             | Price at start of period                 |
| price_end       | FLOAT                      | YES         |             | Price at end of period                   |
| price_high      | FLOAT                      | YES         |             | Highest price in period                  |
| price_low       | FLOAT                      | YES         |             | Lowest price in period                   |
| price_p25       | FLOAT                      | YES         |             | 25th percentile price                    |
| price_median    | FLOAT                      | YES         |             | Median price                             |
| price_p75       | FLOAT                      | YES         |             | 75th percentile price                    |
| price_mean      | FLOAT                      | YES         |             | Mean price                               |
| price_stddev    | FLOAT                      | YES         |             | Std dev of price                         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.analyst_rating_quarterly_summary
**Schema**: `core`
*(Same columns as core.analyst_rating_monthly_summary)*

## Table: core.analyst_rating_yearly_summary
**Schema**: `core`
*(Same columns as core.analyst_rating_monthly_summary)*

## Table: core.revenue_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| event_id        | UUID                       | NO          |             | Reference to earnings event              |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| revenue         | BIGINT                     | YES         |             | Revenue                                  |
| revenue_ttm     | BIGINT                     | YES         |             | TTM Revenue                              |
| revenue_qoq_growth| FLOAT                    | YES         |             | QoQ Revenue Growth                       |
| revenue_qoq_positive_flag| SMALLINT          | YES         |             | Flag for positive QoQ growth             |
| revenue_qoq_count_4q| SMALLINT               | YES         |             | Count of positive QoQ in last 4Q         |
| revenue_qoq_streak_length| SMALLINT          | YES         |             | Streak of positive QoQ growth            |
| revenue_qoq_growth_class| VARCHAR(50)        | YES         |             | Classification of QoQ growth             |
| revenue_qoq_growth_regime| VARCHAR(50)       | YES         |             | Regime of QoQ growth                     |
| revenue_qoq_volatility_4q| FLOAT             | YES         |             | QoQ Volatility (4Q)                      |
| revenue_qoq_volatility_flag| SMALLINT        | YES         |             | Flag for high volatility                 |
| revenue_qoq_growth_drift| FLOAT              | YES         |             | Drift in QoQ growth                      |
| revenue_qoq_outlier_flag| SMALLINT           | YES         |             | Flag for outlier QoQ growth              |
| revenue_qoq_stability_regime| VARCHAR(50)    | YES         |             | Stability regime of QoQ growth           |
| revenue_qoq_accel| FLOAT                     | YES         |             | QoQ Acceleration                         |
| revenue_qoq_accel_count_4q| SMALLINT         | YES         |             | Count of accel in last 4Q                |
| revenue_qoq_accel_positive_flag| SMALLINT    | YES         |             | Flag for positive acceleration           |
| revenue_qoq_accel_streak_length| SMALLINT    | YES         |             | Streak of acceleration                   |
| revenue_qoq_accel_regime| VARCHAR(50)        | YES         |             | Accel regime                             |
| revenue_yoy_growth| FLOAT                    | YES         |             | YoY Revenue Growth                       |
| *(... similar YoY columns as QoQ)*| | | | |
| revenue_ttm_growth| FLOAT                    | YES         |             | TTM Revenue Growth                       |
| *(... similar TTM columns as QoQ)*| | | | |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash                              |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.eps_diluted_metrics
**Schema**: `core`
*(Structure similar to core.revenue_metrics but for EPS Diluted)*

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| event_id        | UUID                       | NO          |             | Reference to earnings event              |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| eps_diluted     | NUMERIC(10,2)              | YES         |             | EPS Diluted                              |
| eps_diluted_ttm | NUMERIC(10,2)              | YES         |             | TTM EPS Diluted                          |
| *(... plus QoQ, YoY, TTM growth/accel/volatility metrics similar to revenue_metrics)* | | | | |

## Table: core.valuation_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date of metrics                          |
| market_cap      | NUMERIC(20, 2)             | YES         |             | Market Capitalization                    |
| pe_ttm          | NUMERIC(20, 6)             | YES         |             | PE Ratio (TTM)                           |
| pe_forward      | NUMERIC(20, 6)             | YES         |             | Forward PE Ratio                         |
| ev_to_ebitda_ttm| NUMERIC(20, 6)             | YES         |             | EV / EBITDA (TTM)                        |
| fcf_yield_ttm   | NUMERIC(20, 8)             | YES         |             | FCF Yield (TTM)                          |
| ps_ttm          | NUMERIC(20, 6)             | YES         |             | Price to Sales (TTM)                     |
| ev_to_revenue_ttm| NUMERIC(20, 6)            | YES         |             | EV / Revenue (TTM)                       |
| p_to_fcf_ttm    | NUMERIC(20, 6)             | YES         |             | Price / FCF (TTM)                        |
| peg_ratio       | NUMERIC(20, 6)             | YES         |             | PEG Ratio                                |
| peg_ratio_forward| NUMERIC(20, 6)            | YES         |             | Forward PEG Ratio                        |
| price_to_book   | NUMERIC(20, 6)             | YES         |             | Price to Book                            |
| ev_to_fcf_ttm   | NUMERIC(20, 6)             | YES         |             | EV / FCF (TTM)                           |
| earnings_yield_ttm| NUMERIC(20, 8)           | YES         |             | Earnings Yield (TTM)                     |
| revenue_yield_ttm| NUMERIC(20, 8)            | YES         |             | Revenue Yield (TTM)                      |
| total_shareholder_yield_ttm| NUMERIC(20, 8)  | YES         |             | Total Shareholder Yield (TTM)            |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.profitability_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date of metrics                          |
| gross_margin    | NUMERIC(20, 8)             | YES         |             | Gross Margin                             |
| operating_margin| NUMERIC(20, 8)             | YES         |             | Operating Margin                         |
| ebitda_margin   | NUMERIC(20, 8)             | YES         |             | EBITDA Margin                            |
| net_margin      | NUMERIC(20, 8)             | YES         |             | Net Margin                               |
| roe             | NUMERIC(20, 8)             | YES         |             | Return on Equity                         |
| roa             | NUMERIC(20, 8)             | YES         |             | Return on Assets                         |
| roic            | NUMERIC(20, 8)             | YES         |             | Return on Invested Capital               |
| ocf_margin      | NUMERIC(20, 8)             | YES         |             | Operating Cash Flow Margin               |
| fcf_margin      | NUMERIC(20, 8)             | YES         |             | Free Cash Flow Margin                    |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.growth_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date of metrics                          |
| revenue_growth_yoy| NUMERIC(20, 8)           | YES         |             | Revenue Growth (YoY)                     |
| revenue_cagr_3y | NUMERIC(20, 8)             | YES         |             | Revenue CAGR (3Y)                        |
| revenue_cagr_5y | NUMERIC(20, 8)             | YES         |             | Revenue CAGR (5Y)                        |
| eps_growth_yoy  | NUMERIC(20, 8)             | YES         |             | EPS Growth (YoY)                         |
| eps_cagr_3y     | NUMERIC(20, 8)             | YES         |             | EPS CAGR (3Y)                            |
| eps_cagr_5y     | NUMERIC(20, 8)             | YES         |             | EPS CAGR (5Y)                            |
| fcf_growth_yoy  | NUMERIC(20, 8)             | YES         |             | FCF Growth (YoY)                         |
| fcf_cagr_3y     | NUMERIC(20, 8)             | YES         |             | FCF CAGR (3Y)                            |
| fcf_cagr_5y     | NUMERIC(20, 8)             | YES         |             | FCF CAGR (5Y)                            |
| ebitda_growth_yoy| NUMERIC(20, 8)            | YES         |             | EBITDA Growth (YoY)                      |
| ebitda_cagr_3y  | NUMERIC(20, 8)             | YES         |             | EBITDA CAGR (3Y)                         |
| ebitda_cagr_5y  | NUMERIC(20, 8)             | YES         |             | EBITDA CAGR (5Y)                         |
| operating_income_growth_yoy| NUMERIC(20, 8)  | YES         |             | Operating Income Growth (YoY)            |
| forward_revenue_growth| NUMERIC(20, 8)       | YES         |             | Forward Revenue Growth                   |
| forward_eps_growth| NUMERIC(20, 8)           | YES         |             | Forward EPS Growth                       |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.efficiency_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date of metrics                          |
| asset_turnover  | NUMERIC(20, 8)             | YES         |             | Asset Turnover                           |
| cash_conversion_cycle| NUMERIC(20, 6)        | YES         |             | Cash Conversion Cycle                    |
| dso             | NUMERIC(20, 6)             | YES         |             | Days Sales Outstanding                   |
| dio             | NUMERIC(20, 6)             | YES         |             | Days Inventory Outstanding               |
| dpo             | NUMERIC(20, 6)             | YES         |             | Days Payable Outstanding                 |
| fixed_asset_turnover| NUMERIC(20, 8)         | YES         |             | Fixed Asset Turnover                     |
| revenue_per_employee| NUMERIC(20, 2)         | YES         |             | Revenue Per Employee                     |
| opex_ratio      | NUMERIC(20, 8)             | YES         |             | Opex Ratio                               |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.financial_health_metrics
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date of metrics                          |
| net_debt_to_ebitda_ttm| NUMERIC(20, 6)       | YES         |             | Net Debt / EBITDA (TTM)                  |
| interest_coverage_ttm| NUMERIC(20, 6)        | YES         |             | Interest Coverage (TTM)                  |
| current_ratio   | NUMERIC(20, 6)             | YES         |             | Current Ratio                            |
| quick_ratio     | NUMERIC(20, 6)             | YES         |             | Quick Ratio                              |
| cash_ratio      | NUMERIC(20, 6)             | YES         |             | Cash Ratio                               |
| debt_to_equity  | NUMERIC(20, 6)             | YES         |             | Debt to Equity                           |
| debt_to_assets  | NUMERIC(20, 6)             | YES         |             | Debt to Assets                           |
| altman_z_score  | NUMERIC(20, 6)             | YES         |             | Altman Z-Score                           |
| cash_runway_months| NUMERIC(20, 2)           | YES         |             | Cash Runway (Months)                     |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.valuation_percentiles
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          |             | Reference to metrics record              |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| date            | DATE                       | NO          |             | Date                                     |
| market_cap_percentile| NUMERIC(6, 3)         | YES         |             | Market Cap Percentile                    |
| pe_ttm_percentile| NUMERIC(6, 3)             | YES         |             | PE (TTM) Percentile                      |
| pe_forward_percentile| NUMERIC(6, 3)         | YES         |             | PE Forward Percentile                    |
| ev_to_ebitda_ttm_percentile| NUMERIC(6, 3)   | YES         |             | EV/EBITDA Percentile                     |
| fcf_yield_ttm_percentile| NUMERIC(6, 3)      | YES         |             | FCF Yield Percentile                     |
| ps_ttm_percentile| NUMERIC(6, 3)             | YES         |             | PS (TTM) Percentile                      |
| ev_to_revenue_ttm_percentile| NUMERIC(6, 3)  | YES         |             | EV/Revenue Percentile                    |
| p_to_fcf_ttm_percentile| NUMERIC(6, 3)       | YES         |             | Price/FCF Percentile                     |
| peg_ratio_percentile| NUMERIC(6, 3)          | YES         |             | PEG Ratio Percentile                     |
| peg_ratio_forward_percentile| NUMERIC(6, 3)  | YES         |             | PEG Forward Percentile                   |
| price_to_book_percentile| NUMERIC(6, 3)      | YES         |             | Price/Book Percentile                    |
| ev_to_fcf_ttm_percentile| NUMERIC(6, 3)      | YES         |             | EV/FCF Percentile                        |
| earnings_yield_ttm_percentile| NUMERIC(6, 3) | YES         |             | Earnings Yield Percentile                |
| revenue_yield_ttm_percentile| NUMERIC(6, 3)  | YES         |             | Revenue Yield Percentile                 |
| total_shareholder_yield_ttm_percentile| NUMERIC(6, 3)| YES   |             | Shareholder Yield Percentile             |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.profitability_percentiles
**Schema**: `core`
*(Contains percentiles for all columns in core.profitability_metrics)*

## Table: core.growth_percentiles
**Schema**: `core`
*(Contains percentiles for all columns in core.growth_metrics)*

## Table: core.efficiency_percentiles
**Schema**: `core`
*(Contains percentiles for all columns in core.efficiency_metrics)*

## Table: core.financial_health_percentiles
**Schema**: `core`
*(Contains percentiles for all columns in core.financial_health_metrics)*

## Table: core.stock_scores
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES         | Date of score                            |
| valuation_score | NUMERIC(6, 3)              | YES         |             | Valuation Score (0-100)                  |
| profitability_score| NUMERIC(6, 3)           | YES         |             | Profitability Score (0-100)              |
| growth_score    | NUMERIC(6, 3)              | YES         |             | Growth Score (0-100)                     |
| efficiency_score| NUMERIC(6, 3)              | YES         |             | Efficiency Score (0-100)                 |
| financial_health_score| NUMERIC(6, 3)        | YES         |             | Financial Health Score (0-100)           |
| total_score     | NUMERIC(6, 3)              | YES         |             | Total Stock Score (0-100)                |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |
