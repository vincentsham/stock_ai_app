# Database Schema Documentation

## Schema: core
**Description**: Stores processed and harmonized data ready for analysis and application usage.

### Tables in `core`
- `stock_profiles`: Canonical stock profiles with summaries.
- `news`: Deduplicated and processed news articles.
- `earnings_calendar`: Future earnings dates and fiscal periods.
- `earnings`: Historical standardized earnings data.
- `earnings_transcripts`: Earnings call transcripts.
- `analyst_price_targets`: Standardized analyst price targets.
- `analyst_grades`: Standardized analyst upgrades/downgrades.
- `income_statements_quarterly`: Standardized quarterly income statements.
- `balance_sheets_quarterly`: Standardized quarterly balance sheets.
- `cash_flow_statements_quarterly`: Standardized quarterly cash flow statements.


## Table: core.stock_profiles
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol (Canonical)          |
| name            | VARCHAR(255)               | YES         |             | Full name of the company                 |
| sector          | VARCHAR(255)               | YES         |             | Sector in which the company operates     |
| industry        | VARCHAR(255)               | YES         |             | Industry classification of the company   |
| country         | VARCHAR(255)               | YES         |             | Country where the company is based       |
| market_cap      | BIGINT                     | YES         |             | Market capitalization of the company     |
| employees       | INTEGER                    | YES         |             | Number of employees in the company       |
| description     | TEXT                       | YES         |             | Brief description of the company         |
| website         | TEXT                       | YES         |             | Official website of the company          |
| exchange        | TEXT                       | YES         |             | Stock exchange where the company is listed |
| currency        | VARCHAR(10)                | YES         |             | Currency used in the company's reports   |
| summary         | TEXT                       | YES         |             | ~200–300 words summary (for LLMs)        |
| short_summary   | TEXT                       | YES         |             | ~80–150 words summary (UI-friendly)      |
| raw_json_sha256 | CHAR(64)                   | YES         |             | Hash of the raw JSON payload             |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.news
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| published_at    | TIMESTAMP                  | NO          |             | Date and time the news was published     |
| publisher       | TEXT                       | YES         |             | Publisher of the news article            |
| title           | TEXT                       | NO          |             | Title of the news article                |
| site            | TEXT                       | YES         |             | Website where the news was published     |
| content         | TEXT                       | YES         |             | Content of the news article              |
| url             | TEXT                       | NO          |             | URL of the news article (Unique per tic) |
| source          | VARCHAR(255)               | YES         |             | Source of the news article               |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_calendar
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| calendar_year   | INT                        | NO          | YES         | Calendar year                            |
| calendar_quarter| INT                        | NO          | YES         | Calendar quarter                         |
| earnings_date   | DATE                       | YES         |             | Scheduled earnings date                  |
| fiscal_year     | INT                        | YES         |             | Fiscal year                              |
| fiscal_quarter  | INT                        | YES         |             | Fiscal quarter                           |
| fiscal_date     | DATE                       | YES         |             | Fiscal period end date                   |
| session         | VARCHAR(10)                | YES         |             | Trading session                          |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| earnings_date   | DATE                       | NO          |             | Date of the earnings report              |
| fiscal_year     | SMALLINT                   | YES         |             | Fiscal year                              |
| fiscal_quarter  | SMALLINT                   | YES         |             | Fiscal quarter                           |
| fiscal_date     | DATE                       | YES         |             | Fiscal period end date                   |
| session         | VARCHAR(10)                | YES         |             | Trading session                          |
| eps             | NUMERIC(10,4)              | YES         |             | Earnings per share                       |
| eps_estimated   | NUMERIC(10,4)              | YES         |             | Estimated earnings per share             |
| revenue         | NUMERIC(20,2)              | YES         |             | Total revenue                            |
| revenue_estimated| NUMERIC(20,2)             | YES         |             | Estimated revenue                        |
| source          | VARCHAR(255)               | YES         |             | Source of the data                       |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_transcripts
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| earnings_date   | DATE                       | NO          |             | Date of the earnings call                |
| transcript      | TEXT                       | NO          |             | Full transcript text                     |
| transcript_sha256| CHAR(64)                  | NO          |             | Hashed transcript content                |
| source          | VARCHAR(255)               | YES         |             | Source of the transcript                 |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.analyst_price_targets
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| published_at    | TIMESTAMP                  | NO          |             | Date published                           |
| title           | TEXT                       | YES         |             | Article title                            |
| site            | TEXT                       | YES         |             | Site name                                |
| analyst_name    | TEXT                       | YES         |             | Name of analyst                          |
| company         | TEXT                       | YES         |             | Analyst firm/company                     |
| price_target    | NUMERIC(12,2)              | YES         |             | Target price                             |
| adj_price_target| NUMERIC(12,2)              | YES         |             | Adjusted target price                    |
| price_when_posted| NUMERIC(12,4)             | YES         |             | Price at time of posting                 |
| url             | TEXT                       | NO          |             | Source URL (Unique per tic)              |
| source          | VARCHAR(255)               | YES         |             | Source system                            |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.analyst_grades
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| published_at    | TIMESTAMP                  | NO          |             | Date published                           |
| title           | TEXT                       | YES         |             | Article title                            |
| site            | TEXT                       | YES         |             | Site name                                |
| company         | TEXT                       | YES         |             | Grading company                          |
| new_grade       | SMALLINT                   | YES         |             | New numerical grade                      |
| previous_grade  | SMALLINT                   | YES         |             | Previous numerical grade                 |
| action          | TEXT                       | YES         |             | Upgrade/Downgrade/etc.                   |
| price_when_posted| NUMERIC(12,4)             | YES         |             | Price at time of posting                 |
| url             | TEXT                       | NO          |             | Source URL (Unique per tic)              |
| source          | VARCHAR(255)               | YES         |             | Source system                            |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.income_statements_quarterly
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| earnings_date   | DATE                       | NO          |             | Period end date (company fiscal)         |
| fiscal_year     | SMALLINT                   | NO          |             | Fiscal year                              |
| fiscal_quarter  | SMALLINT                   | NO          |             | Fiscal quarter                           |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| revenue         | NUMERIC(20, 2)             | YES         |             | Revenue                                  |
| cost_of_revenue | NUMERIC(20, 2)             | YES         |             | Cost of Revenue                          |
| gross_profit    | NUMERIC(20, 2)             | YES         |             | Gross Profit                             |
| research_and_development | NUMERIC(20, 2)    | YES         |             | R&D Expenses                             |
| selling_general_admin | NUMERIC(20, 2)       | YES         |             | SG&A Expenses                            |
| depreciation_amortization | NUMERIC(20, 2)   | YES         |             | D&A Expenses                             |
| operating_expenses | NUMERIC(20, 2)          | YES         |             | Total Operating Expenses                 |
| operating_income| NUMERIC(20, 2)             | YES         |             | Operating Income                         |
| ebitda          | NUMERIC(20, 2)             | YES         |             | EBITDA                                   |
| ebit            | NUMERIC(20, 2)             | YES         |             | EBIT                                     |
| interest_income | NUMERIC(20, 2)             | YES         |             | Interest Income                          |
| interest_expense| NUMERIC(20, 2)             | YES         |             | Interest Expense                         |
| other_non_operating_income | NUMERIC(20, 2)  | YES         |             | Other Non-Operating Income               |
| income_before_tax | NUMERIC(20, 2)           | YES         |             | Income Before Tax                        |
| income_tax_expense | NUMERIC(20, 2)          | YES         |             | Income Tax Expense                       |
| effective_tax_rate | NUMERIC(10, 6)          | YES         |             | Effective Tax Rate                       |
| net_income      | NUMERIC(20, 2)             | YES         |             | Net Income                               |
| weighted_average_shares_basic | NUMERIC(20, 2)| YES        |             | Basic Shares Outstanding                 |
| weighted_average_shares_diluted | NUMERIC(20, 2)| YES      |             | Diluted Shares Outstanding               |
| eps             | NUMERIC(10, 4)             | YES         |             | EPS                                      |
| eps_diluted     | NUMERIC(10, 4)             | YES         |             | Diluted EPS                              |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.balance_sheets_quarterly
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| earnings_date   | DATE                       | NO          |             | Period end date (company fiscal)         |
| fiscal_year     | SMALLINT                   | NO          |             | Fiscal year                              |
| fiscal_quarter  | SMALLINT                   | NO          |             | Fiscal quarter                           |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| total_assets    | NUMERIC(20, 2)             | YES         |             | Total Assets                             |
| total_current_assets | NUMERIC(20, 2)        | YES         |             | Total Current Assets                     |
| cash_and_short_term_investments | NUMERIC(20, 2)| YES      |             | Cash & Short Term Investments            |
| cash_and_cash_equivalents | NUMERIC(20, 2)   | YES         |             | Cash & Cash Equivalents                  |
| accounts_receivable | NUMERIC(20, 2)         | YES         |             | Accounts Receivable                      |
| inventory       | NUMERIC(20, 2)             | YES         |             | Inventory                                |
| net_ppe         | NUMERIC(20, 2)             | YES         |             | Net Property, Plant, Equipment           |
| goodwill_and_intangibles | NUMERIC(20, 2)    | YES         |             | Goodwill & Intangibles                   |
| total_liabilities | NUMERIC(20, 2)           | YES         |             | Total Liabilities                        |
| total_current_liabilities | NUMERIC(20, 2)   | YES         |             | Total Current Liabilities                |
| accounts_payable | NUMERIC(20, 2)            | YES         |             | Accounts Payable                         |
| deferred_revenue_current | NUMERIC(20, 2)    | YES         |             | Deferred Revenue (Current)               |
| deferred_revenue_non_current | NUMERIC(20, 2)| YES         |             | Deferred Revenue (Non-Current)           |
| total_debt      | NUMERIC(20, 2)             | YES         |             | Total Debt                               |
| long_term_debt  | NUMERIC(20, 2)             | YES         |             | Long Term Debt                           |
| current_debt_and_capital_lease | NUMERIC(20, 2)| YES       |             | Current Debt & Capital Lease             |
| total_equity    | NUMERIC(20, 2)             | YES         |             | Total Equity                             |
| retained_earnings | NUMERIC(20, 2)           | YES         |             | Retained Earnings                        |
| common_stock    | NUMERIC(20, 2)             | YES         |             | Common Stock                             |
| working_capital | NUMERIC(20, 2)             | YES         |             | Working Capital                          |
| invested_capital| NUMERIC(20, 2)             | YES         |             | Invested Capital                         |
| net_tangible_assets | NUMERIC(20, 2)         | YES         |             | Net Tangible Assets                      |
| ordinary_shares_number | NUMERIC(20, 2)      | YES         |             | Ordinary Shares Number                   |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |

## Table: core.cash_flow_statements_quarterly
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Unique identifier                        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| earnings_date   | DATE                       | NO          |             | Period end date (company fiscal)         |
| fiscal_year     | SMALLINT                   | NO          |             | Fiscal year                              |
| fiscal_quarter  | SMALLINT                   | NO          |             | Fiscal quarter                           |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| net_income      | NUMERIC(20, 2)             | YES         |             | Net Income                               |
| depreciation_amortization | NUMERIC(20, 2)   | YES         |             | Depreciation & Amortization              |
| stock_based_compensation | NUMERIC(20, 2)    | YES         |             | Stock Based Compensation                 |
| deferred_income_tax | NUMERIC(20, 2)         | YES         |             | Deferred Income Tax                      |
| change_in_working_capital | NUMERIC(20, 2)   | YES         |             | Change in Working Capital                |
| change_in_receivables | NUMERIC(20, 2)       | YES         |             | Change in Receivables                    |
| change_in_inventory | NUMERIC(20, 2)         | YES         |             | Change in Inventory                      |
| change_in_accounts_payable | NUMERIC(20, 2)  | YES         |             | Change in Accounts Payable               |
| operating_cash_flow | NUMERIC(20, 2)         | YES         |             | Operating Cash Flow                      |
| capital_expenditure | NUMERIC(20, 2)         | YES         |             | Capital Expenditure                      |
| acquisitions_net | NUMERIC(20, 2)            | YES         |             | Acquisitions Net                         |
| investments_purchases | NUMERIC(20, 2)       | YES         |             | Investments Purchases                    |
| investments_sales | NUMERIC(20, 2)           | YES         |             | Investments Sales                        |
| investing_cash_flow | NUMERIC(20, 2)         | YES         |             | Investing Cash Flow                      |
| net_debt_issuance | NUMERIC(20, 2)           | YES         |             | Net Debt Issuance                        |
| common_stock_repurchased | NUMERIC(20, 2)    | YES         |             | Common Stock Repurchased                 |
| dividends_paid  | NUMERIC(20, 2)             | YES         |             | Dividends Paid                           |
| financing_cash_flow | NUMERIC(20, 2)         | YES         |             | Financing Cash Flow                      |
| free_cash_flow  | NUMERIC(20, 2)             | YES         |             | Free Cash Flow                           |
| net_change_in_cash | NUMERIC(20, 2)          | YES         |             | Net Change in Cash                       |
| end_cash_position | NUMERIC(20, 2)           | YES         |             | End Cash Position                        |
| income_tax_paid | NUMERIC(20, 2)             | YES         |             | Income Tax Paid                          |
| interest_paid   | NUMERIC(20, 2)             | YES         |             | Interest Paid                            |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | NO          |             | Timestamp of the last update             |
