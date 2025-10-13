# Database Schema Documentation


## Schema: core
**Description**: Stores processed and structured data derived from raw data.

### Tables in `core`
- `stock_profiles`: Contains processed metadata about stocks.
- `news_analysis`: Stores analysis data derived from news articles.
- `earnings_transcript_chunks`: Stores chunked data from earnings transcripts.
- `earnings_transcript_embeddings`: Contains embeddings for earnings transcript chunks.
- `earnings_transcript_analysis`: Contains analysis data derived from earnings transcripts.


## Table: stock_profiles
**Description**: Contains processed metadata about stocks.

**Schema**: `core`

**Source**: `raw.stock_profiles`

**Script**: `company_profile_summarizer/main.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| name            | character varying          | YES         |             | Full name of the company                 |
| sector          | character varying          | YES         |             | Sector in which the company operates     |
| industry        | character varying          | YES         |             | Industry classification of the company   |
| country         | character varying          | YES         |             | Country where the company is based       |
| market_cap      | bigint                     | YES         |             | Market capitalization of the company     |
| employees       | integer                    | YES         |             | Number of employees in the company       |
| description     | text                       | YES         |             | Brief description of the company         |
| website         | text                       | YES         |             | Official website of the company          |
| exchange        | text                       | YES         |             | Stock exchange where the company is listed |
| currency        | character varying          | YES         |             | Currency used in the company's reports   |
| summary         | text                       | YES         |             | Summary of the company                   |
| short_summary   | text                       | YES         |             | Short summary of the company             |
| raw_json_sha256 | character                 | YES         |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |


## Table: news_analysis
**Description**: Stores analysis data derived from news articles.

**Schema**: `core`

**Source**: `raw.news`

**Script**: `news_ai_agent/main.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| url             | text                       | NO          | YES         | URL of the news article                  |
| title           | text                       | NO          |             | Title of the news article                |
| content         | text                       | YES         |             | Content of the news article              |
| publisher       | text                       | YES         |             | Publisher of the news article            |
| published_date  | timestamp without time zone| NO          |             | Date and time the news was published     |
| category        | character varying          | YES         |             | Category of the news                     |
| event_type      | text                       | YES         |             | Type of event                            |
| time_horizon    | integer                    | YES         |             | Time horizon of the event                |
| duration        | text                       | YES         |             | Duration of the event                    |
| impact_magnitude| integer                    | YES         |             | Magnitude of the impact                  |
| affected_dimensions| ARRAY                  | YES         |             | Affected dimensions                      |
| sentiment       | integer                    | YES         |             | Sentiment score                          |
| raw_json_sha256 | character                 | NO          |             | SHA256 hash of the raw JSON data         |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |



## Table: earnings_transcript_chunks
**Description**: Stores chunked data from earnings transcripts.

**Schema**: `core`

**Source**: `raw.earnings_transcipts`

**Script**: `earnings_transcript_chunking/chunk_earnings_transcripts.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings transcript   |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings transcript|
| earnings_date   | date                       | YES         |             | Date of the earnings                     |
| chunk_id        | integer                    | NO          | YES         | ID of the chunk                          |
| chunk           | text                       | NO          |             | Content of the chunk                     |
| token_count     | integer                    | NO          |             | Token count of the chunk                 |
| chunk_sha256    | text                       | NO          |             | SHA256 hash of the chunk                 |
| transcript_sha256| text                      | NO          |             | SHA256 hash of the transcript            |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: earnings_transcript_embeddings
**Description**: Contains embeddings for earnings transcript chunks.

**Schema**: `core`

**Source**: `core.earnings_transcript_chunks`

**Script**: `earnings_transcript_chunking/embed_earnings_transcripts.py`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year     | integer                    | NO          | YES         | Fiscal year of the earnings transcript   |
| fiscal_quarter  | integer                    | NO          | YES         | Fiscal quarter of the earnings transcript|
| earnings_date   | date                       | YES         |             | Date of the earnings                     |
| chunk_id        | integer                    | NO          | YES         | ID of the chunk                          |
| chunk_sha256    | text                       | NO          |             | SHA256 hash of the chunk                 |
| transcript_sha256| text                      | NO          |             | SHA256 hash of the transcript            |
| embedding       | USER-DEFINED              | NO          |             | Embedding vector                         |
| embedding_model | text                       | NO          |             | Model used for embedding                 |
| updated_at      | timestamp with time zone   | YES         |             | Timestamp of the last update             |

## Table: earnings_transcript_analysis
**Description**: Contains analysis data derived from earnings transcripts.

**Schema**: `core`

**Source**: `core.earnings_transcripts_chunks`, `core.earnings_transcripts_embeddings`

**Script**: `earnings_transcript_ai_agent/main.py`

| Column Name              | Data Type                  | Is Nullable | Primary Key | Description                              |
|--------------------------|----------------------------|-------------|-------------|------------------------------------------|
| tic                      | character varying          | NO          | YES         | Stock ticker symbol                      |
| fiscal_year              | integer                    | NO          | YES         | Fiscal year of the earnings transcript   |
| fiscal_quarter           | integer                    | NO          | YES         | Fiscal quarter of the earnings transcript|
| sentiment                | smallint                  | YES         |             | Sentiment score                          |
| durability               | smallint                  | YES         |             | Durability score                         |
| performance_factors      | ARRAY                     | NO          |             | Performance factors                      |
| past_summary             | text                      | YES         |             | Summary of past performance              |
| guidance_direction       | smallint                  | YES         |             | Direction of guidance                    |
| revenue_outlook          | smallint                  | YES         |             | Revenue outlook                          |
| margin_outlook           | smallint                  | YES         |             | Margin outlook                           |
| earnings_outlook         | smallint                  | YES         |             | Earnings outlook                         |
| cashflow_outlook         | smallint                  | YES         |             | Cashflow outlook                         |
| growth_acceleration      | smallint                  | YES         |             | Growth acceleration                      |
| future_outlook_sentiment | smallint                  | YES         |             | Sentiment for future outlook             |
| catalysts                | ARRAY                     | NO          |             | Catalysts                                |
| future_summary           | text                      | YES         |             | Summary of future outlook                |
| risk_mentioned           | smallint                  | YES         |             | Whether risks were mentioned             |
| risk_impact              | smallint                  | YES         |             | Impact of risks                          |
| risk_time_horizon        | smallint                  | YES         |             | Time horizon for risks                   |
| risk_factors             | ARRAY                     | NO          |             | Risk factors                             |
| risk_summary             | text                      | YES         |             | Summary of risks                         |
| mitigation_mentioned     | smallint                  | YES         |             | Whether mitigations were mentioned       |
| mitigation_effectiveness | smallint                  | YES         |             | Effectiveness of mitigations             |
| mitigation_time_horizon  | smallint                  | YES         |             | Time horizon for mitigations             |
| mitigation_actions       | ARRAY                     | NO          |             | Mitigation actions                       |
| mitigation_summary       | text                      | YES         |             | Summary of mitigations                   |
| transcript_sha256        | text                      | NO          |             | SHA256 hash of the transcript            |
| updated_at               | timestamp with time zone  | YES         |             | Timestamp of the last update             |



