# Database Schema Documentation

## Table: stock_metadata
**Description**: Contains metadata about stocks, such as industry, sector, and market information.

**Source**: `yfinance`

**Script**: `load_stock_metadata.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| name            | character varying          | YES         |             |
| description     | text                       | YES         |             |
| sector          | character varying          | YES         |             |
| industry        | character varying          | YES         |             |
| employees       | integer                    | YES         |             |
| market_cap      | bigint                     | YES         |             |
| country         | character varying          | YES         |             |
| currency        | character varying          | YES         |             |
| exchange        | character varying          | YES         |             |
| website         | character varying          | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: stock_ohlcv
**Description**: Stores historical OHLCV (Open, High, Low, Close, Volume) data for stocks.

**Source**: `yfinance`

**Script**: `load_stock_ohlcv.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| date            | date                       | NO          | YES         |
| open            | double precision           | NO          |             |
| high            | double precision           | NO          |             |
| low             | double precision           | NO          |             |
| close           | double precision           | NO          |             |
| volume          | bigint                     | NO          |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: earnings
**Description**: Contains earnings data, including EPS, revenue, and session information.

**Source**: `CoinCodex API`

**Script**: `load_historical_earnings.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| fiscal_year     | integer                    | NO          | YES         |
| fiscal_quarter  | integer                    | NO          | YES         |
| fiscal_date     | date                       | NO          |             |
| earnings_date   | date                       | NO          |             |
| eps             | double precision           | YES         |             |
| eps_estimated   | double precision           | YES         |             |
| revenue         | bigint                     | YES         |             |
| revenue_estimated| bigint                    | YES         |             |
| price_before    | double precision           | YES         |             |
| price_after     | double precision           | YES         |             |
| session         | character varying          | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: earnings_transcripts
**Description**: Stores transcripts of earnings calls for companies.

**Source**: `API Ninjas Earnings Transcript API`

**Script**: `load_earnings_transcripts.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| fiscal_year     | integer                    | NO          | YES         |
| fiscal_quarter  | integer                    | NO          | YES         |
| earnings_date   | date                       | NO          |             |
| raw_json        | jsonb                      | YES         |             |
| source          | text                       | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: cash_flows
**Description**: Contains cash flow statement data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_cash_flows.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| fiscal_year     | integer                    | NO          | YES         |
| fiscal_quarter  | integer                    | NO          | YES         |
| fiscal_date     | date                       | NO          |             |
| raw_json        | jsonb                      | NO          |             |
| source          | text                       | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: balance_sheets
**Description**: Stores balance sheet data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_balance_sheets.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| fiscal_year     | integer                    | NO          | YES         |
| fiscal_quarter  | integer                    | NO          | YES         |
| fiscal_date     | date                       | NO          |             |
| raw_json        | jsonb                      | NO          |             |
| source          | text                       | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |

## Table: income_statements
**Description**: Contains income statement data for companies.

**Source**: `Financial Modeling Prep API`

**Script**: `load_income_statements.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key |
|-----------------|----------------------------|-------------|-------------|
| tic             | character varying          | NO          | YES         |
| fiscal_year     | integer                    | NO          | YES         |
| fiscal_quarter  | integer                    | NO          | YES         |
| fiscal_date     | date                       | NO          |             |
| raw_json        | jsonb                      | NO          |             |
| source          | text                       | YES         |             |
| last_updated    | timestamp without time zone| YES         |             |