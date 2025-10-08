from psycopg import connect
from utils import connect_to_db

# Connect to PostgreSQL
def table_creation(conn):
    try:
        cursor = conn.cursor()


        # Test the connection by executing a simple query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print("Connection test successful!")
        else:
            print("Connection test failed!")

        # Create a table for stock metadata if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.stock_metadata (
            tic VARCHAR(10) PRIMARY KEY,
            name VARCHAR(255),
            sector VARCHAR(255),
            industry VARCHAR(255),
            country VARCHAR(255),
            market_cap BIGINT,
            employees INTEGER,
            description TEXT,
            website VARCHAR(255),
            exchange VARCHAR(255),
            currency VARCHAR(10),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("Table 'stock_metadata' created or already exists.")


        # Create a table for stock OHLCV data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.stock_ohlcv (
            date DATE NOT NULL,
            tic VARCHAR(10) NOT NULL,
            open FLOAT NOT NULL,
            high FLOAT NOT NULL,
            low FLOAT NOT NULL,
            close FLOAT NOT NULL,
            volume BIGINT NOT NULL,
            last_updated    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date, tic)
        );
        """)
        print("Table 'stock_ohlcv' created or already exists.")


        # Create a table for historical earnings data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.earnings (
            tic VARCHAR(20) NOT NULL,
            fiscal_year INT NOT NULL,
            fiscal_quarter INT NOT NULL,
            fiscal_date DATE NOT NULL,              
            earnings_date DATE NOT NULL,
            eps FLOAT,
            eps_estimated FLOAT,
            session VARCHAR(10),
            revenue BIGINT,
            revenue_estimated BIGINT,
            price_before FLOAT,
            price_after FLOAT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'earnings' created or already exists with composite primary key.")


        # Create a table for historical earnings transcripts data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.earnings_transcripts (
            tic             VARCHAR(20)  NOT NULL,
            fiscal_year     INT          NOT NULL,
            fiscal_quarter  INT          NOT NULL,
            earnings_date   DATE         NOT NULL,
            transcript      TEXT,
            transcript_hash TEXT,
            raw_json        JSONB,   -- renamed from payload
            source          TEXT DEFAULT 'api-ninjas/earningstranscript',
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'earnings_transcripts' created or already exists with composite primary key.")


        # Create a table for income statements if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.income_statements (
            tic             VARCHAR(20)  NOT NULL,                 -- e.g., AAPL
            fiscal_year     INT          NOT NULL,                 -- e.g., 2025
            fiscal_quarter  INT          NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date     DATE         NOT NULL,
            raw_json        JSONB        NOT NULL,                 -- full original payload
            source          TEXT,
            last_updated    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'income_statements' created or already exists with composite primary key.")

        # Create a table for cash flows if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.cash_flows (
            tic             VARCHAR(20)  NOT NULL,                 -- e.g., AAPL
            fiscal_year     INT          NOT NULL,                 -- e.g., 2025
            fiscal_quarter  INT          NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date     DATE         NOT NULL,
            raw_json        JSONB        NOT NULL,                 -- full original payload
            source          TEXT,
            last_updated    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'cash_flows' created or already exists with composite primary key.")

        # Create a table for balance sheets if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.balance_sheets (
            tic             VARCHAR(20)  NOT NULL,                 -- e.g., AAPL
            fiscal_year     INT          NOT NULL,                 -- e.g., 2025
            fiscal_quarter  INT          NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date     DATE         NOT NULL,
            raw_json        JSONB        NOT NULL,                 -- full original payload
            source          TEXT,
            last_updated    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'balance_sheets' created or already exists with composite primary key.")

        # Create a table for news data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.news (
            tic             VARCHAR(20) NOT NULL,              -- stock ticker
            published_date  TIMESTAMP   NOT NULL,              -- from API publishedDate
            publisher       TEXT,
            title           TEXT NOT NULL,
            site            TEXT,
            content         TEXT,
            url             TEXT NOT NULL,
            raw_json        JSONB,
            source          TEXT,
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tic, url)             -- composite PK: unique news per ticker+url
        );
        """)
        print("Table 'news' created or already exists with composite primary key.")



        # Create a table for news analysis if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news_analysis (
            tic             VARCHAR(20) NOT NULL,              -- stock ticker
            url             TEXT NOT NULL,                    -- URL of the news article
            title           TEXT NOT NULL,                    -- Title of the news article
            content         TEXT,                             -- Content of the news article
            publisher       TEXT,                             -- Publisher of the news article
            published_date  TIMESTAMP NOT NULL,               -- Date and time the news was published
            category        VARCHAR(50),                      -- Category of the news (e.g., fundamental, technical)
            event_type      TEXT,                             -- Type of event described in the news
            time_horizon    VARCHAR(50),                      -- Time horizon of the impact (e.g., short_term)
            duration        TEXT,                             -- Duration of the impact
            impact_magnitude VARCHAR(50),                    -- Magnitude of the impact (e.g., minor, major)
            affected_dimensions TEXT[],                      -- List of affected dimensions (e.g., revenue, profit)
            sentiment       VARCHAR(50),                     -- Sentiment analysis result (e.g., positive, negative)
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of the last update
            PRIMARY KEY (tic, url)                           -- Composite PK: unique analysis per ticker+url
        );
        """)
        print("Table 'news_analysis' created or already exists with composite primary key.")


        # Create a table for earnings transcript chunks if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcript_chunks (
            -- Transcript identity
            tic             VARCHAR(20) NOT NULL,
            fiscal_year     INT NOT NULL,
            fiscal_quarter  INT NOT NULL,
            earnings_date   DATE,

            -- Sequential id within a single transcript (1..N)
            chunk_id        INT NOT NULL,

            -- Chunk content
            chunk           TEXT NOT NULL,
            token_count     INT,
            -- optional integrity/lineage
            chunk_hash      TEXT,
            transcript_hash TEXT,

            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (tic, fiscal_year, fiscal_quarter, chunk_id)
        );
        """)
        print("Table 'earnings_transcript_chunks' created or already exists with composite primary key.")

        # Create a full-text index for keyword/BM25 search
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_core_earnings_transcripts_chunks_tsv
          ON core.earnings_transcript_chunks
          USING GIN (to_tsvector('english', chunk));
        """)
        print("Index 'idx_core_earnings_transcripts_chunks_tsv' created or already exists.")


        # Ensure the vector extension is available
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("Extension 'vector' created or already exists.")
        
        # Create a table for earnings transcript embeddings if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcript_embeddings (
            tic             VARCHAR(20) NOT NULL,
            fiscal_year     INT NOT NULL,
            fiscal_quarter  INT NOT NULL,
            earnings_date   DATE,

            -- Sequential id within a single transcript (1..N)
            chunk_id        INT NOT NULL,

            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (tic, fiscal_year, fiscal_quarter, chunk_id),
            FOREIGN KEY (tic, fiscal_year, fiscal_quarter, chunk_id)
                REFERENCES core.earnings_transcript_chunks (tic, fiscal_year, fiscal_quarter, chunk_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'earnings_transcript_embeddings' created or already exists with composite primary key.")

        # Create an HNSW index for the embeddings
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_core_earnings_transcript_embeddings_vec_hnsw
          ON core.earnings_transcript_embeddings
          USING hnsw (embedding vector_cosine_ops)
          WITH (m = 16, ef_construction = 200);
        """)
        print("Index 'idx_core_earnings_transcript_embeddings_vec_hnsw' created or already exists.")


        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            print("Tables created successfully!")
            conn.close()


if __name__ == "__main__":
    conn = connect_to_db()
    table_creation(conn)