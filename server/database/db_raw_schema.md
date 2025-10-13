# Database Schema Documentation


## Schema: raw
**Description**: Stores raw data ingested from various sources.

### Tables in `raw`
- `stock_profiles`: Contains profiles about stocks, such as industry, sector, and market information.
- `stock_ohlcv`: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.
- `earnings`: Contains earnings data, including EPS, revenue, and session information.
- `earnings_transcripts`: Stores transcripts of earnings calls for companies.
- `cash_flows`: Contains cash flow statement data for companies.
- `balance_sheets`: Stores balance sheet data for companies.
- `income_statements`: Contains income statement data for companies.
- `news`: Stores news articles related to stocks.
- `analyst_price_targets`: Contains analyst price target data for stocks.
- `analyst_grades`: Contains analyst grades data for stocks.


## Table: raw.stock_profiles
**Description**: Contains profiles about stocks, such as industry, sector, and market information.

**Schema**: `raw`

**Source**: `yfinance`

**Script**: `extract_stock_profiles.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| name            | character varying          | YES         |             | Full name of the company                 |
| sector          | character varying          | YES         |             | Sector in which the company operates     |
| industry        | character varying          | YES         |             | Industry classification of the company   |
| country         | character varying          | YES         |             | Country where the company is based       |
| description     | text                       | YES         |             | Brief description of the company         |
| website         | text                       | YES         |             | Official website of the company          |
| market_cap      | bigint                     | YES         |             | Market capitalization of the company     |
| employees       | integer                    | YES         |             | Number of employees in the company       |
| currency        | character varying          | YES         |             | Currency used in the company's reports   |
| exchange        | text                       | YES         |             | Stock exchange where the company is listed |
| source          | text                       | YES         |             | Source of the data                       |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the stock profile       |
| raw_json_sha256 | character                  | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: stock_ohlcv 
**Description**: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.

**Schema**: `raw`

**Source**: `yfinance`

**Script**: `extract_stock_ohlcv.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| date            | date                       | NO          | YES         | Date of the OHLCV data                   |
| open            | numeric                    | NO          |             | Opening price of the stock               |
| high            | numeric                    | NO          |             | Highest price of the stock during the day|
| low             | numeric                    | NO          |             | Lowest price of the stock during the day |
| close           | numeric                    | NO          |             | Closing price of the stock               |
| volume          | bigint                     | NO          |             | Trading volume of the stock              |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: earnings 
**Description**: Contains earnings data, including EPS, revenue, and session information.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`, `CoinCodex API`

**Script**: `extract_earnings.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings data         |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings data      |
| fiscal_date     | date                       | YES         |             | Fiscal date of the earnings data         |
| earnings_date   | date                       | NO          |             | Date of the earnings report              |
| session         | character varying          | YES         |             | Trading session (e.g., pre-market)       |
| eps             | numeric(10,4)             | YES         |             | Earnings per share                       |
| eps_estimated   | numeric(10,4)             | YES         |             | Estimated earnings per share             |
| revenue         | numeric(20,2)             | YES         |             | Total revenue of the company             |
| revenue_estimated| numeric(20,2)            | YES         |             | Estimated revenue of the company         |
| price_before    | numeric(12,4)             | YES         |             | Stock price before the earnings report   |
| price_after     | numeric(12,4)             | YES         |             | Stock price after the earnings report    |
| source          | text                       | YES         |             | Source of the earnings data              |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the earnings            |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: earnings_transcripts 
**Description**: Stores transcripts of earnings calls for companies.

**Schema**: `raw`

**Source**: `API Ninjas Earnings Transcript API`

**Script**: `extract_earnings_transcripts.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings call         |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings call      |
| earnings_date   | date                       | NO          |             | Date of the earnings call                |
| transcript      | text                       | NO          |             | Transcript of the earnings call          |
| transcript_sha256 | character                | NO          |             | SHA256 hash of the transcript            |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the transcript          |
| raw_json_sha256 | character                  | NO          |             | SHA256 hash of the raw JSON data         |
| source          | text                       | YES         |             | Source of the transcript                 |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: cash_flows 
**Description**: Contains cash flow statement data for companies.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_cash_flows.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(20)     | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the cash flow data        |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the cash flow data     |
| source          | text                       | YES         |             | Source of the cash flow data             |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the cash flow statement |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: balance_sheets 
**Description**: Stores balance sheet data for companies.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_balance_sheets.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(20)     | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES      | Fiscal year of the balance sheet data  |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the balance sheet data |
| source          | text                       | YES         |             | Source of the balance sheet data    |
| raw_json        | jsonb                      | NO          |          | Raw JSON data of the balance sheet statement |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: income_statements 
**Description**: Contains income statement data for companies.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_income_statements.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(20)     | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the income statement data |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the income statement data |
| source          | text                       | YES         |             | Source of the income statement data      |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the income statement    |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: news 
**Description**: Stores news articles related to stocks.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_news.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(20)     | NO          | YES         | Stock ticker symbol                      |
| published_date  | timestamp with time zone  | NO          | YES         | Date and time the news was published     |
| publisher       | text                       | YES         |             | Publisher of the news article            |
| title           | text                       | NO          |             | Title of the news article                |
| site            | text                       | YES         |             | Website where the news was published     |
| content         | text                       | YES         |             | Content of the news article              |
| url             | text                       | NO          | YES         | URL of the news article                  |
| source          | text                       | YES         |             | Source of the news article               |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the news article        |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: analyst_price_targets
**Description**: Contains analyst price target data for stocks.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_analyst_price_targets.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(10)     | NO          | YES         | Stock ticker symbol                      |
| published_at    | timestamp with time zone  | NO          |             | Date and time the price target was published |
| news_title      | text                       | YES         |             | Title of the related news article        |
| news_base_url   | text                       | YES         |             | Base URL of the news article             |
| news_publisher  | text                       | YES         |             | Publisher of the news article            |
| analyst_name    | text                       | YES         |             | Name of the analyst                      |
| broker          | text                       | YES         |             | Broker associated with the analyst       |
| price_target    | numeric(12,2)             | YES         |             | Analyst's price target                   |
| adj_price_target| numeric(12,2)             | YES         |             | Adjusted price target                    |
| price_when_posted| numeric(12,4)            | YES         |             | Stock price when the price target was posted |
| url             | text                       | NO          | YES         | URL of the news article                  |
| source          | text                       | YES         |             | Source of the price target data          |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the price target        |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: analyst_grades
**Description**: Contains analyst grades data for stocks.

**Schema**: `raw`

**Source**: `Financial Modeling Prep API`

**Script**: `extract_analyst_grades.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying(10)     | NO          | YES         | Stock ticker symbol                      |
| published_at    | timestamp with time zone  | NO          |             | Date and time the grade was published    |
| news_title      | text                       | YES         |             | Title of the related news article        |
| news_base_url   | text                       | YES         |             | Base URL of the news article             |
| news_publisher  | text                       | YES         |             | Publisher of the news article            |
| new_grade       | text                       | YES         |             | New grade assigned by the analyst        |
| previous_grade  | text                       | YES         |             | Previous grade assigned by the analyst   |
| grading_company | text                       | YES         |             | Company responsible for the grading      |
| action          | text                       | YES         |             | Action taken (e.g., upgrade, downgrade)  |
| price_when_posted| numeric(12,4)            | YES         |             | Stock price when the grade was posted    |
| url             | text                       | NO          | YES         | URL of the news article                  |
| source          | text                       | YES         |             | Source of the grade data                 |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the grade               |
| raw_json_sha256 | character(64)             | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |