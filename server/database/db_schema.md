# Database Schema Documentation

## List of Tables
- `stock_metadata`: Contains metadata about stocks, such as industry, sector, and market information.
- `stock_ohlcv`: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.
- `earnings`: Contains earnings data, including EPS, revenue, and session information.
- `earnings_transcripts`: Stores transcripts of earnings calls for companies.
- `cash_flows`: Contains cash flow statement data for companies.
- `balance_sheets`: Stores balance sheet data for companies.
- `income_statements`: Contains income statement data for companies.

## Table: stock_metadata
**Description**: Contains metadata about stocks, such as industry, sector, and market information.

**Source**: `yfinance`

**Script**: `load_stock_metadata.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| name            | character varying          | YES         |             | Full name of the company                 |
| description     | text                       | YES         |             | Brief description of the company         |
| sector          | character varying          | YES         |             | Sector in which the company operates     |
| industry        | character varying          | YES         |             | Industry classification of the company   |
| employees       | integer                    | YES         |             | Number of employees in the company       |
| market_cap      | bigint                     | YES         |             | Market capitalization of the company     |
| country         | character varying          | YES         |             | Country where the company is based       |
| currency        | character varying          | YES         |             | Currency used in the company's reports   |
| exchange        | character varying          | YES         |             | Stock exchange where the company is listed |
| website         | character varying          | YES         |             | Official website of the company          |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: stock_ohlcv
**Description**: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.

**Source**: `yfinance`

**Script**: `load_stock_ohlcv.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| date            | date                       | NO          | YES         | Date of the OHLCV data                   |
| open            | double precision           | NO          |             | Opening price of the stock               |
| high            | double precision           | NO          |             | Highest price of the stock during the day|
| low             | double precision           | NO          |             | Lowest price of the stock during the day |
| close           | double precision           | NO          |             | Closing price of the stock               |
| volume          | bigint                     | NO          |             | Trading volume of the stock              |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: earnings
**Description**: Contains earnings data, including EPS, revenue, and session information.

**Source**: `CoinCodex API`

**Script**: `load_historical_earnings.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings data         |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings data      |
| fiscal_date     | date                       | NO          |             | Fiscal date of the earnings data         |
| earnings_date   | date                       | NO          |             | Date of the earnings report              |
| eps             | double precision           | YES         |             | Earnings per share                       |
| eps_estimated   | double precision           | YES         |             | Estimated earnings per share             |
| revenue         | bigint                     | YES         |             | Total revenue of the company             |
| revenue_estimated| bigint                    | YES         |             | Estimated revenue of the company         |
| price_before    | double precision           | YES         |             | Stock price before the earnings report   |
| price_after     | double precision           | YES         |             | Stock price after the earnings report    |
| session         | character varying          | YES         |             | Trading session (e.g., pre-market)       |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: earnings_transcripts
**Description**: Stores transcripts of earnings calls for companies.

**Source**: `API Ninjas Earnings Transcript API`

**Script**: `load_earnings_transcripts.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings call         |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings call      |
| earnings_date   | date                       | NO          |             | Date of the earnings call                |
| raw_json        | jsonb                      | YES         |             | Raw JSON data of the transcript          |
| source          | text                       | YES         |             | Source of the transcript                 |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: cash_flows
**Description**: Contains cash flow statement data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_cash_flows.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the cash flow data        |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the cash flow data     |
| fiscal_date     | date                       | NO          |             | Fiscal date of the cash flow data        |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the cash flow statement |
| source          | text                       | YES         |             | Source of the cash flow data             |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: balance_sheets
**Description**: Stores balance sheet data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_balance_sheets.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the balance sheet data    |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the balance sheet data |
| fiscal_date     | date                       | NO          |             | Fiscal date of the balance sheet data    |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the balance sheet       |
| source          | text                       | YES         |             | Source of the balance sheet data         |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |

## Table: income_statements
**Description**: Contains income statement data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_income_statements.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the income statement data |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the income statement data |
| fiscal_date     | date                       | NO          |             | Fiscal date of the income statement data |
| raw_json        | jsonb                      | NO          |             | Raw JSON data of the income statement    |
| source          | text                       | YES         |             | Source of the income statement data      |
| last_updated    | timestamp without time zone| YES         |             | Timestamp of the last update             |