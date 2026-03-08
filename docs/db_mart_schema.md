# Database Schema Documentation

## Schema: mart
**Description**: Stores high-level, aggregated, and versioned data ready for consumption by the web application and AI agents. Designed for fast retrieval and historical point-in-time analysis.

### Tables in `mart`
- `stock_profiles`: Canonical stock profiles with versioning.
- `earnings`: Historical earnings data with growth metrics.
- `earnings_regime`: Classification of earnings performance (surprises, growth regimes).
- `earnings_transcript_analysis`: AI-driven analysis of earnings transcripts.
- `analyst_rating_yearly_summary`: Aggregated analyst ratings and price targets over time.
- `catalyst_master`: Master list of catalysts with metadata.
- `valuation_metrics`: Valuation ratios and percentiles.
- `profitability_metrics`: Profitability margins and returns.
- `growth_metrics`: Historical and forward-looking growth rates.
- `efficiency_metrics`: Operational efficiency ratios.
- `financial_health_metrics`: Balance sheet and liquidity metrics.
- `stock_scores`: Composite scores for stock ranking.

## Table: mart.stock_profiles
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | YES         |             | Stock ticker symbol                      |
| name            | VARCHAR(255)               | YES         |             | Company name                             |
| sector          | VARCHAR(255)               | YES         |             | Sector                                   |
| industry        | VARCHAR(255)               | YES         |             | Industry                                 |
| country         | VARCHAR(255)               | YES         |             | Country                                  |
| market_cap      | BIGINT                     | YES         |             | Market Capitalization                    |
| employees       | INTEGER                    | YES         |             | Number of employees                      |
| description     | TEXT                       | YES         |             | Detailed description                     |
| website         | TEXT                       | YES         |             | Website URL                              |
| exchange        | TEXT                       | YES         |             | Stock exchange                           |
| currency        | VARCHAR(10)                | YES         |             | Reporting currency                       |
| summary         | TEXT                       | YES         |             | AI Summary (~200-300 words)              |
| short_summary   | TEXT                       | YES         |             | Short Summary (~80-150 words)            |
| raw_json_sha256 | CHAR(64)                   | YES         |             | Data lineage hash                        |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, as_of_date)*

## Table: mart.earnings
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar Year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar Quarter                         |
| earnings_date   | DATE                       | NO          |             | Earnings release date                    |
| eps             | NUMERIC(10,4)              | YES         |             | Actual EPS                               |
| eps_estimated   | NUMERIC(10,4)              | YES         |             | Estimated EPS                            |
| eps_yoy_growth  | NUMERIC(10,4)              | YES         |             | EPS YoY Growth                           |
| eps_yoy_acceleration| NUMERIC(10,4)          | YES         |             | EPS YoY Acceleration                     |
| revenue         | NUMERIC(20,2)              | YES         |             | Actual Revenue                           |
| revenue_estimated| NUMERIC(20,2)             | YES         |             | Estimated Revenue                        |
| revenue_yoy_growth| NUMERIC(10,4)            | YES         |             | Revenue YoY Growth                       |
| revenue_yoy_acceleration| NUMERIC(10,4)      | YES         |             | Revenue YoY Acceleration                 |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, calendar_year, calendar_quarter, as_of_date)*

## Table: mart.earnings_regime
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar Year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar Quarter                         |
| earnings_date   | DATE                       | NO          |             | Earnings release date                    |
| eps_surprise_regime | VARCHAR(50)            | YES         |             | EPS Surprise Classification              |
| revenue_surprise_regime| VARCHAR(50)         | YES         |             | Revenue Surprise Classification          |
| eps_yoy_growth_regime| VARCHAR(50)           | YES         |             | EPS YoY Growth Regime                    |
| revenue_yoy_growth_regime| VARCHAR(50)       | YES         |             | Revenue YoY Growth Regime                |
| eps_yoy_accel_regime| VARCHAR(50)            | YES         |             | EPS Acceleration Regime                  |
| revenue_yoy_accel_regime| VARCHAR(50)        | YES         |             | Revenue Acceleration Regime              |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, calendar_year, calendar_quarter, as_of_date)*

## Table: mart.earnings_transcript_analysis
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference run ID                         |
| event_id        | UUID                       | NO          | YES*        | Transcript event ID                      |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar Year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar Quarter                         |
| earnings_date   | DATE                       | NO          |             | Earnings release date                    |
| sentiment       | SMALLINT                   | YES         |             | Overall Sentiment Score (-1, 0, 1)       |
| durability      | SMALLINT                   | YES         |             | Durability Score                         |
| performance_factors| TEXT[]                  | NO          |             | Key performance drivers                  |
| past_summary    | TEXT                       | YES         |             | Summary of past performance              |
| guidance_direction| SMALLINT                 | YES         |             | Guidance Trend                           |
| revenue_outlook | SMALLINT                   | YES         |             | Revenue Outlook                          |
| margin_outlook  | SMALLINT                   | YES         |             | Margin Outlook                           |
| earnings_outlook| SMALLINT                   | YES         |             | Earnings Outlook                         |
| cashflow_outlook| SMALLINT                   | YES         |             | Cashflow Outlook                         |
| growth_acceleration| SMALLINT                | YES         |             | Growth Acceleration Signal               |
| future_outlook_sentiment| SMALLINT           | YES         |             | Future Sentiment Score                   |
| growth_drivers  | TEXT[]                     | NO          |             | Future growth drivers                    |
| future_summary  | TEXT                       | YES         |             | Summary of future outlook                |
| risk_mentioned  | SMALLINT                   | YES         |             | Risk Mentioned Flag                      |
| risk_impact     | SMALLINT                   | YES         |             | Risk Impact Score                        |
| risk_time_horizon| SMALLINT                  | YES         |             | Risk Time Horizon                        |
| risk_factors    | TEXT[]                     | NO          |             | Identified Risk Factors                  |
| risk_summary    | TEXT                       | YES         |             | Summary of risks                         |
| mitigation_mentioned| SMALLINT               | YES         |             | Mitigation Mentioned Flag                |
| mitigation_effectiveness| SMALLINT           | YES         |             | Mitigation Effectiveness Note            |
| mitigation_time_horizon| SMALLINT            | YES         |             | Mitigation Time Horizon                  |
| mitigation_actions| TEXT[]                   | NO          |             | Mitigation Actions                       |
| mitigation_summary| TEXT                     | YES         |             | Summary of mitigations                   |
| transcript_sha256| CHAR(64)                  | NO          |             | Transcript Hash                          |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, calendar_year, calendar_quarter, as_of_date) and (event_id, as_of_date)*

## Table: mart.analyst_rating_yearly_summary
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| close           | NUMERIC(12,4)              | YES         |             | Closing price on date                    |
| pt_count        | INTEGER                    | YES         |             | Number of price targets                  |
| pt_high         | NUMERIC(12,4)              | YES         |             | Highest price target                     |
| pt_low          | NUMERIC(12,4)              | YES         |             | Lowest price target                      |
| pt_p25          | NUMERIC(12,4)              | YES         |             | 25th percentile target                   |
| pt_median       | NUMERIC(12,4)              | YES         |             | Median price target                      |
| pt_p75          | NUMERIC(12,4)              | YES         |             | 75th percentile target                   |
| pt_upgrade_n    | INTEGER                    | YES         |             | Count of PT upgrades                     |
| pt_downgrade_n  | INTEGER                    | YES         |             | Count of PT downgrades                   |
| pt_reiterate_n  | INTEGER                    | YES         |             | Count of PT reiterations                 |
| pt_init_n       | INTEGER                    | YES         |             | Count of PT initiations                  |
| grade_count     | INTEGER                    | YES         |             | Total grade count                        |
| grade_buy_n     | INTEGER                    | YES         |             | Buy grades count                         |
| grade_hold_n    | INTEGER                    | YES         |             | Hold grades count                        |
| grade_sell_n    | INTEGER                    | YES         |             | Sell grades count                        |
| grade_upgrade_n | INTEGER                    | YES         |             | Grade upgrades count                     |
| grade_downgrade_n| INTEGER                   | YES         |             | Grade downgrades count                   |
| grade_reiterate_n| INTEGER                   | YES         |             | Grade reiterations count                 |
| grade_init_n    | INTEGER                    | YES         |             | Grade initiations count                  |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.catalyst_master
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| catalyst_id     | UUID                       | YES         | YES*        | Catalyst ID                              |
| tic             | VARCHAR(10)                | YES         |             | Stock ticker symbol                      |
| date            | DATE                       | YES         |             | Estimated event date                     |
| catalyst_type   | VARCHAR(64)                | YES         |             | Type classification                      |
| title           | TEXT                       | YES         |             | Catalyst title                           |
| summary         | TEXT                       | YES         |             | Detailed summary                         |
| state           | VARCHAR(20)                | YES         |             | Current state (e.g. active)              |
| sentiment       | SMALLINT                   | YES         |             | Sentiment score                          |
| time_horizon    | SMALLINT                   | YES         |             | Time horizon estimate                    |
| magnitude.      | SMALLINT                   | YES         |             | Impact magnitude estimate                |
| certainty       | VARCHAR(20)                | YES         |             | Certainty level                          |
| impact_area     | VARCHAR(32)                | YES         |             | Business area impacted                   |
| mention_count   | INTEGER                    | YES         |             | Frequency mentioned                      |
| event_ids       | TEXT[]                     | YES         |             | Linked event IDs                         |
| source_types    | TEXT[]                     | YES         |             | Types of sources                         |
| evidences       | TEXT[]                     | YES         |             | Extracted evidence snippets              |
| urls            | TEXT[]                     | YES         |             | Source URLs                              |
| created_at      | TIMESTAMPTZ                | YES         |             | Creation timestamp                       |
| updated_at      | TIMESTAMPTZ                | YES         |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (catalyst_id, as_of_date)*

## Table: mart.valuation_metrics
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference ID                             |
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| score           | NUMERIC(6,3)               | YES         |             | Overall Valuation Score (0-100)          |
| pe_ttm          | NUMERIC(20,6)              | YES         |             | Price / EPS (TTM)                        |
| pe_forward      | NUMERIC(20,6)              | YES         |             | Price / Forward EPS                      |
| ev_to_ebitda_ttm| NUMERIC(20,6)              | YES         |             | EV / EBITDA (TTM)                        |
| fcf_yield_ttm   | NUMERIC(20,8)              | YES         |             | FCF / Market Cap (TTM)                   |
| ps_ttm          | NUMERIC(20,6)              | YES         |             | Price / Sales (TTM)                      |
| ev_to_revenue_ttm| NUMERIC(20,6)             | YES         |             | EV / Revenue (TTM)                       |
| p_to_fcf_ttm    | NUMERIC(20,6)              | YES         |             | Price / Free Cash Flow (TTM)             |
| peg_ratio       | NUMERIC(20,6)              | YES         |             | PEG Ratio                                |
| peg_ratio_forward| NUMERIC(20,6)             | YES         |             | Forward PEG Ratio                        |
| price_to_book   | NUMERIC(20,6)              | YES         |             | Price / Book                             |
| ev_to_fcf_ttm   | NUMERIC(20,6)              | YES         |             | EV / FCF (TTM)                           |
| earnings_yield_ttm| NUMERIC(20,8)            | YES         |             | Earnings Yield                           |
| revenue_yield_ttm| NUMERIC(20,8)             | YES         |             | Revenue Yield                            |
| total_shareholder_yield_ttm| NUMERIC(20,8)   | YES         |             | Total Shareholder Yield                  |
| *_percentile    | NUMERIC(6,3)               | YES         |             | Percentile ranks for all metrics         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.profitability_metrics
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference ID                             |
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| score           | NUMERIC(6,3)               | YES         |             | Overall Profitability Score (0-100)      |
| gross_margin    | NUMERIC(20,8)              | YES         |             | Gross Margin                             |
| operating_margin| NUMERIC(20,8)              | YES         |             | Operating Margin                         |
| ebitda_margin   | NUMERIC(20,8)              | YES         |             | EBITDA Margin                            |
| net_margin      | NUMERIC(20,8)              | YES         |             | Net Margin                               |
| roe             | NUMERIC(20,8)              | YES         |             | Return on Equity (ROE)                   |
| roa             | NUMERIC(20,8)              | YES         |             | Return on Assets (ROA)                   |
| roic            | NUMERIC(20,8)              | YES         |             | Return on Invested Capital (ROIC)        |
| ocf_margin      | NUMERIC(20,8)              | YES         |             | OCF Margin                               |
| fcf_margin      | NUMERIC(20,8)              | YES         |             | FCF Margin                               |
| *_percentile    | NUMERIC(6,3)               | YES         |             | Percentile ranks for all metrics         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.growth_metrics
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference ID                             |
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| score           | NUMERIC(6,3)               | YES         |             | Overall Growth Score (0-100)             |
| revenue_growth_yoy| NUMERIC(20,8)            | YES         |             | Revenue Growth YOY                       |
| revenue_cagr_3y | NUMERIC(20,8)              | YES         |             | Revenue CAGR 3Y                          |
| revenue_cagr_5y | NUMERIC(20,8)              | YES         |             | Revenue CAGR 5Y                          |
| eps_growth_yoy  | NUMERIC(20,8)              | YES         |             | EPS Growth YOY                           |
| eps_cagr_3y     | NUMERIC(20,8)              | YES         |             | EPS CAGR 3Y                              |
| eps_cagr_5y     | NUMERIC(20,8)              | YES         |             | EPS CAGR 5Y                              |
| fcf_growth_yoy  | NUMERIC(20,8)              | YES         |             | FCF Growth YOY                           |
| fcf_cagr_3y     | NUMERIC(20,8)              | YES         |             | FCF CAGR 3Y                              |
| fcf_cagr_5y     | NUMERIC(20,8)              | YES         |             | FCF CAGR 5Y                              |
| ebitda_growth_yoy| NUMERIC(20,8)             | YES         |             | EBITDA Growth YOY                        |
| ebitda_cagr_3y  | NUMERIC(20,8)              | YES         |             | EBITDA CAGR 3Y                           |
| ebitda_cagr_5y  | NUMERIC(20,8)              | YES         |             | EBITDA CAGR 5Y                           |
| operating_income_growth_yoy| NUMERIC(20,8)   | YES         |             | Operating Income Growth YOY              |
| forward_revenue_growth| NUMERIC(20,8)        | YES         |             | Forward Revenue Growth                   |
| forward_eps_growth| NUMERIC(20,8)            | YES         |             | Forward EPS Growth                       |
| *_percentile    | NUMERIC(6,3)               | YES         |             | Percentile ranks for all metrics         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.efficiency_metrics
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference ID                             |
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| score           | NUMERIC(6,3)               | YES         |             | Overall Efficiency Score (0-100)         |
| asset_turnover  | NUMERIC(20,8)              | YES         |             | Asset Turnover                           |
| cash_conversion_cycle| NUMERIC(20,6)         | YES         |             | Cash Conversion Cycle                    |
| dso             | NUMERIC(20,6)              | YES         |             | Days Sales Outstanding (DSO)             |
| dio             | NUMERIC(20,6)              | YES         |             | Days Inventory Outstanding (DIO)         |
| dpo             | NUMERIC(20,6)              | YES         |             | Days Payables Outstanding (DPO)          |
| fixed_asset_turnover| NUMERIC(20,8)          | YES         |             | Fixed Asset Turnover                     |
| revenue_per_employee| NUMERIC(20,2)          | YES         |             | Revenue Per Employee                     |
| opex_ratio      | NUMERIC(20,8)              | YES         |             | Operating Expense Ratio                  |
| *_percentile    | NUMERIC(6,3)               | YES         |             | Percentile ranks for all metrics         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.financial_health_metrics
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | YES         |             | Inference ID                             |
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| score           | NUMERIC(6,3)               | YES         |             | Overall Financial Health Score (0-100)   |
| net_debt_to_ebitda_ttm| NUMERIC(20,6)        | YES         |             | Net Debt / EBITDA (TTM)                  |
| interest_coverage_ttm| NUMERIC(20,6)         | YES         |             | Interest Coverage (TTM)                  |
| current_ratio   | NUMERIC(20,6)              | YES         |             | Current Ratio                            |
| quick_ratio     | NUMERIC(20,6)              | YES         |             | Quick Ratio                              |
| cash_ratio      | NUMERIC(20,6)              | YES         |             | Cash Ratio                               |
| debt_to_equity  | NUMERIC(20,6)              | YES         |             | Debt to Equity                           |
| debt_to_assets  | NUMERIC(20,6)              | YES         |             | Debt to Assets                           |
| altman_z_score  | NUMERIC(20,6)              | YES         |             | Altman Z-Score                           |
| *_percentile    | NUMERIC(6,3)               | YES         |             | Percentile ranks for all metrics         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*

## Table: mart.stock_scores
**Schema**: `mart`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES*        | Stock ticker symbol                      |
| date            | DATE                       | NO          | YES*        | Snapshot date                            |
| valuation_score | NUMERIC(6,3)               | YES         |             | Valuation Score (0-100)                  |
| profitability_score| NUMERIC(6,3)            | YES         |             | Profitability Score (0-100)              |
| growth_score    | NUMERIC(6,3)               | YES         |             | Growth Score (0-100)                     |
| efficiency_score| NUMERIC(6,3)               | YES         |             | Efficiency Score (0-100)                 |
| financial_health_score| NUMERIC(6,3)         | YES         |             | Financial Health Score (0-100)           |
| total_score     | NUMERIC(6,3)               | YES         |             | Total Comprehensive Score (0-100)        |
| updated_at      | TIMESTAMPTZ                | NO          |             | Last update timestamp                    |
| as_of_date      | DATE                       | NO          | YES*        | Data validity date (Part of Unique Key)  |

*\*Unique Constraint: (tic, date, as_of_date)*
