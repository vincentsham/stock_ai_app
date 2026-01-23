# Database Schema Documentation

## Schema: raw
**Description**: Stores raw data ingested from various sources.

### Tables in `raw`
- `stock_profiles`: Contains profiles about stocks, such as industry, sector, and market information.
- `stock_ohlcv_daily`: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.
- `earnings`: Contains earnings data, including EPS, revenue, and session information.
- `earnings_transcripts`: Stores transcripts of earnings calls for companies.
- `income_statements_quarterly`: Contains quarterly income statement data.
- `cash_flow_statements_quarterly`: Contains quarterly cash flow statement data.
- `balance_sheets_quarterly`: Stores quarterly balance sheet data.
- `news`: Stores news articles related to stocks.
- `analyst_price_targets`: Contains analyst price target data.
- `analyst_grades`: Contains analyst grades data.


## Table: raw.stock_profiles
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
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
| source          | VARCHAR(255)               | YES         |             | Source of the data                       |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the stock profile       |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.stock_ohlcv_daily
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| date            | DATE                       | NO          | YES         | Date of the OHLCV data                   |
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| open            | NUMERIC(12,4)              | NO          |             | Opening price of the stock               |
| high            | NUMERIC(12,4)              | NO          |             | Highest price of the stock during the day|
| low             | NUMERIC(12,4)              | NO          |             | Lowest price of the stock during the day |
| close           | NUMERIC(12,4)              | NO          |             | Closing price of the stock               |
| volume          | BIGINT                     | NO          |             | Trading volume of the stock              |
| source          | VARCHAR(255)               | YES         |             | Source of the data                       |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.earnings
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| calendar_year   | INT                        | NO          | YES         | Calendar year of the earnings data       |
| calendar_quarter| SMALLINT                   | NO          | YES         | Calendar quarter of the earnings data    |
| earnings_date   | DATE                       | NO          |             | Date of the earnings report              |
| fiscal_date     | DATE                       | YES         |             | Fiscal date                              |
| session         | VARCHAR(10)                | YES         |             | Trading session (e.g., pre-market)       |
| eps             | NUMERIC(10,4)              | YES         |             | Earnings per share                       |
| eps_estimated   | NUMERIC(10,4)              | YES         |             | Estimated earnings per share             |
| revenue         | NUMERIC(20,2)              | YES         |             | Total revenue of the company             |
| revenue_estimated| NUMERIC(20,2)             | YES         |             | Estimated revenue of the company         |
| source          | VARCHAR(255)               | YES         |             | Source of the earnings data              |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the earnings            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.earnings_transcripts
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| calendar_year   | INT                        | NO          | YES         | Calendar year of the earnings call       |
| calendar_quarter| SMALLINT                   | NO          | YES         | Calendar quarter of the earnings call    |
| earnings_date   | DATE                       | NO          |             | Date of the earnings call                |
| url             | TEXT                       | NO          |             | URL of the transcript                    |
| source          | VARCHAR(255)               | YES         |             | Source of the transcript                 |
| raw_json        | JSONB                      | NO          |             | Raw JSON data                            |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| transcript_sha256| CHAR(64)                  | NO          |             | SHA256 hash of the transcript content    |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.income_statements_quarterly
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | INT                        | NO          | YES         | Fiscal year of the income statement data |
| fiscal_quarter  | SMALLINT                   | NO          | YES         | Fiscal quarter of the income statement data |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| source          | VARCHAR(255)               | YES         | YES         | Source of the income statement data      |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the income statement    |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.cash_flow_statements_quarterly
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | INT                        | NO          | YES         | Fiscal year of the cash flow data        |
| fiscal_quarter  | SMALLINT                   | NO          | YES         | Fiscal quarter of the cash flow data     |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| source          | VARCHAR(255)               | YES         | YES         | Source of the cash flow data             |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the cash flow statement |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.balance_sheets_quarterly
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | INT                        | NO          | YES         | Fiscal year of the balance sheet data    |
| fiscal_quarter  | SMALLINT                   | NO          | YES         | Fiscal quarter of the balance sheet data |
| fiscal_date     | DATE                       | NO          |             | Fiscal date                              |
| source          | VARCHAR(255)               | YES         | YES         | Source of the balance sheet data         |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the balance sheet       |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.news
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| url             | TEXT                       | NO          | YES         | URL of the news article                  |
| source          | VARCHAR(255)               | YES         |             | Source of the news article               |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the news article        |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.analyst_price_targets
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| url             | TEXT                       | NO          | YES         | URL of the news article/source           |
| source          | VARCHAR(255)               | YES         |             | Source of the price target data          |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the price target        |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: raw.analyst_grades
**Schema**: `raw`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          | YES         | Stock ticker symbol                      |
| url             | TEXT                       | NO          | YES         | URL of the news article/source           |
| source          | VARCHAR(255)               | YES         |             | Source of the grade data                 |
| raw_json        | JSONB                      | NO          |             | Raw JSON data of the grade               |
| raw_json_sha256 | CHAR(64)                   | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |
