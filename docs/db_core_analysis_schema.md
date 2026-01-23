# Database Schema Documentation

## Schema: core
**Description**: Stores analysis results, embeddings, and derived insights from unstructured data (news, transcripts).

### Tables in `core` (Analysis & Embeddings)
- `news_chunks`: Chunks of news articles for processing.
- `news_embeddings`: Vector embeddings of news chunks.
- `news_chunk_signal`: Signal classification for news chunks.
- `news_analysis`: High-level analysis of news articles.
- `earnings_transcript_chunks`: Chunks of earnings transcripts.
- `earnings_transcript_embeddings`: Vector embeddings of transcript chunks.
- `earnings_transcript_chunk_signal`: Signal classification for transcript chunks.
- `earnings_transcript_analysis`: Comprehensive analysis of earnings transcripts.
- `catalyst_master`: Master list of identified catalysts.
- `catalyst_versions`: Extracted catalyst instances and versions.
- `catalyst_master_embeddings`: Embeddings for master catalysts.
- `catalyst_version_embeddings`: Embeddings for catalyst versions.


## Table: core.news_chunks
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| published_at    | TIMESTAMP                  | NO          |             | Date and time the news was published     |
| url             | TEXT                       | NO          |             | URL of the news article                  |
| event_id        | UUID                       | NO          | YES         | Reference to the news event              |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk           | TEXT                       | NO          |             | Text content of the chunk                |
| token_count     | INT                        | NO          |             | Token count of the chunk                 |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| raw_json_sha256 | CHAR(64)                   | NO          |             | Hash of the raw JSON payload             |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.news_embeddings
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| published_at    | TIMESTAMP                  | NO          |             | Date and time the news was published     |
| url             | TEXT                       | NO          |             | URL of the news article                  |
| event_id        | UUID                       | NO          | YES         | Reference to the news event              |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| raw_json_sha256 | CHAR(64)                   | NO          |             | Hash of the raw JSON payload             |
| embedding       | VECTOR(1536)               | NO          |             | Embedding vector                         |
| embedding_model | TEXT                       | NO          |             | Model used for embedding                 |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.news_chunk_signal
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| event_id        | UUID                       | NO          | YES         | Reference to the news event              |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| raw_json_sha256 | CHAR(64)                   | NO          |             | Hash of the raw JSON payload             |
| is_signal       | SMALLINT                   | NO          |             | 1 if signal, 0 if noise                  |
| reason          | TEXT                       | YES         |             | Reason for classification                |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.news_analysis
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier for analysis           |
| event_id        | UUID                       | NO          |             | Reference to the news event              |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| url             | TEXT                       | NO          |             | URL of the news article                  |
| title           | TEXT                       | NO          |             | Title of the news article                |
| content         | TEXT                       | YES         |             | Content of the news article              |
| publisher       | TEXT                       | YES         |             | Publisher of the news article            |
| published_at    | TIMESTAMP                  | NO          |             | Date and time from API                   |
| category        | VARCHAR(50)                | YES         |             | News category (Fundamental/Technical)    |
| event_type      | TEXT                       | YES         |             | Type of event                            |
| time_horizon    | SMALLINT                   | YES         |             | Time horizon classification              |
| duration        | TEXT                       | YES         |             | Duration of impact                       |
| impact_magnitude| SMALLINT                   | YES         |             | Magnitude of impact                      |
| affected_dimensions| TEXT[]                  | YES         |             | Affected financial dimensions            |
| sentiment       | SMALLINT                   | YES         |             | Sentiment score                          |
| raw_json_sha256 | CHAR(64)                   | NO          |             | Hash of the raw JSON payload             |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_transcript_chunks
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| event_id        | UUID                       | NO          | YES         | Reference to the transcript event        |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk           | TEXT                       | NO          |             | Text content of the chunk                |
| token_count     | INT                        | NO          |             | Token count of the chunk                 |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| transcript_sha256| CHAR(64)                  | NO          |             | Hash of the full transcript              |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_transcript_embeddings
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| event_id        | UUID                       | NO          | YES         | Reference to the transcript event        |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| transcript_sha256| CHAR(64)                  | NO          |             | Hash of the full transcript              |
| embedding       | VECTOR(1536)               | NO          |             | Embedding vector                         |
| embedding_model | TEXT                       | NO          |             | Model used for embedding                 |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_transcript_chunk_signal
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| event_id        | UUID                       | NO          | YES         | Reference to the transcript event        |
| chunk_id        | INT                        | NO          | YES         | Sequential ID of the chunk               |
| chunk_sha256    | CHAR(64)                   | NO          |             | Hash of the chunk content                |
| transcript_sha256| CHAR(64)                  | NO          |             | Hash of the full transcript              |
| is_signal       | SMALLINT                   | NO          |             | 1 if signal, 0 if noise                  |
| reason          | TEXT                       | YES         |             | Reason for classification                |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.earnings_transcript_analysis
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| inference_id    | UUID                       | NO          | YES         | Unique identifier for analysis           |
| event_id        | UUID                       | NO          |             | Reference to the transcript event        |
| tic             | VARCHAR(10)                | NO          |             | Stock ticker symbol                      |
| calendar_year   | SMALLINT                   | NO          |             | Calendar year                            |
| calendar_quarter| SMALLINT                   | NO          |             | Calendar quarter                         |
| sentiment       | SMALLINT                   | YES         |             | Overall sentiment score                  |
| durability      | SMALLINT                   | YES         |             | Durability assessments                   |
| performance_factors| TEXT[]                  | YES         |             | Factors impacting performance            |
| past_summary    | TEXT                       | YES         |             | Summary of past performance              |
| guidance_direction| SMALLINT                 | YES         |             | Direction of guidance                    |
| revenue_outlook | SMALLINT                   | YES         |             | Revenue outlook                          |
| margin_outlook  | SMALLINT                   | YES         |             | Margin outlook                           |
| earnings_outlook| SMALLINT                   | YES         |             | Earnings outlook                         |
| cashflow_outlook| SMALLINT                   | YES         |             | Cashflow outlook                         |
| growth_acceleration| SMALLINT                | YES         |             | Growth acceleration                      |
| future_outlook_sentiment| SMALLINT           | YES         |             | Sentiment of future outlook              |
| growth_drivers  | TEXT[]                     | YES         |             | Drivers of growth                        |
| future_summary  | TEXT                       | YES         |             | Summary of future outlook                |
| risk_mentioned  | SMALLINT                   | YES         |             | 1 if risks mentioned, 0 otherwise        |
| risk_impact     | SMALLINT                   | YES         |             | Impact of risks                          |
| risk_time_horizon| SMALLINT                  | YES         |             | Risk time horizon                        |
| risk_factors    | TEXT[]                     | YES         |             | Risk factors                             |
| risk_summary    | TEXT                       | YES         |             | Summary of risks                         |
| mitigation_mentioned| SMALLINT               | YES         |             | 1 if mitigation mentioned                |
| mitigation_effectiveness| SMALLINT           | YES         |             | Effectiveness of mitigation              |
| mitigation_time_horizon| SMALLINT            | YES         |             | Mitigation time horizon                  |
| mitigation_actions| TEXT[]                   | YES         |             | Mitigation actions                       |
| mitigation_summary| TEXT                     | YES         |             | Summary of mitigation                    |
| transcript_sha256| CHAR(64)                  | NO          |             | Hash of the transcript                   |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.catalyst_master
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| catalyst_id     | UUID                       | NO          | YES         | Unique identifier for catalyst           |
| tic             | VARCHAR(10)                | YES         |             | Stock ticker symbol                      |
| date            | DATE                       | YES         |             | Catalyst date                            |
| catalyst_type   | VARCHAR(64)                | YES         |             | Type of catalyst                         |
| title           | TEXT                       | YES         |             | Title of catalyst                        |
| summary         | TEXT                       | YES         |             | Summary of catalyst                      |
| state           | VARCHAR(20)                | YES         |             | State of catalyst (e.g., active)         |
| sentiment       | SMALLINT                   | YES         |             | Sentiment analysis result                |
| time_horizon    | SMALLINT                   | YES         |             | Time horizon                             |
| impact_magnitude| SMALLINT                   | YES         |             | Magnitude of impact                      |
| certainty       | VARCHAR(20)                | YES         |             | Certainty level                          |
| impact_area     | VARCHAR(32)                | YES         |             | Area of impact                           |
| mention_count   | INTEGER                    | YES         |             | Number of times mentioned                |
| event_ids       | TEXT[]                     | YES         |             | List of related event IDs                |
| created_at      | TIMESTAMPTZ                | YES         |             | Timestamp of creation                    |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.catalyst_versions
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Reference to the source event            |
| chunk_id        | INT                        | NO          | YES         | Chunk ID where catalyst was found        |
| catalyst_id     | UUID                       | NO          | YES         | Reference to the master catalyst         |
| tic             | VARCHAR(10)                | YES         |             | Stock ticker symbol                      |
| date            | DATE                       | YES         |             | Date associated with the version         |
| catalyst_type   | VARCHAR(64)                | YES         |             | Type of catalyst                         |
| title           | TEXT                       | YES         |             | Title of catalyst version                |
| summary         | TEXT                       | YES         |             | Summary of catalyst version              |
| evidence        | TEXT                       | YES         |             | Evidence text from chunk                 |
| state           | VARCHAR(20)                | YES         |             | State                                    |
| sentiment       | SMALLINT                   | YES         |             | Sentiment                                |
| time_horizon    | SMALLINT                   | YES         |             | Time horizon                             |
| impact_magnitude| SMALLINT                   | YES         |             | Impact magnitude                         |
| certainty       | VARCHAR(20)                | YES         |             | Certainty                                |
| impact_area     | VARCHAR(32)                | YES         |             | Impact area                              |
| is_valid        | SMALLINT                   | YES         |             | Validation flag                          |
| rejection_reason| TEXT                       | YES         |             | Reason if rejected                       |
| ingestion_batch | VARCHAR(10)                | YES         |             | Ingestion batch ID                       |
| source_type     | VARCHAR(20)                | YES         |             | Type of source                           |
| source          | TEXT                       | YES         |             | Source name                              |
| url             | TEXT                       | YES         |             | Source URL                               |
| raw_json_sha256 | CHAR(64)                   | NO          |             | Hash of raw JSON                         |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.catalyst_master_embeddings
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| catalyst_id     | UUID                       | NO          | YES         | Reference to the master catalyst         |
| embedding       | VECTOR(1536)               | NO          |             | Embedding vector                         |
| embedding_model | TEXT                       | NO          |             | Model used for embedding                 |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |

## Table: core.catalyst_version_embeddings
**Schema**: `core`

| Column Name     | Data Type                  | Is Nullable | Primary Key | Description                              |
|-----------------|----------------------------|-------------|-------------|------------------------------------------|
| event_id        | UUID                       | NO          | YES         | Reference to the source event            |
| chunk_id        | INT                        | NO          | YES         | Reference to the chunk ID                |
| catalyst_id     | UUID                       | NO          | YES         | Reference to the master catalyst         |
| catalyst_type   | VARCHAR(64)                | NO          |             | Type of catalyst                         |
| embedding       | VECTOR(1536)               | NO          |             | Embedding vector                         |
| embedding_model | TEXT                       | NO          |             | Model used for embedding                 |
| updated_at      | TIMESTAMPTZ                | YES         |             | Timestamp of the last update             |
