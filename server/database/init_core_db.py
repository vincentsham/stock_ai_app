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


        # Create schema 'core' if it does not exist
        cursor.execute("""CREATE SCHEMA IF NOT EXISTS core;""")
        print("Schema 'core' created or already exists.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.stock_profiles (
            tic             VARCHAR(10) PRIMARY KEY,      -- one canonical record per ticker
            name            VARCHAR(255),
            sector          VARCHAR(255),
            industry        VARCHAR(255),
            country         VARCHAR(255),
            market_cap      BIGINT,                
            employees       INTEGER,
            description     TEXT,
            website         TEXT,
            exchange        TEXT,
            currency        VARCHAR(10),
            summary         TEXT,                         -- ~200–300 words (for LLMs)
            short_summary   TEXT,                         -- ~80–150 words (UI-friendly)
            raw_json_sha256 CHAR(64),               -- hash of the raw JSON payload for integrity/lineage
            updated_at      TIMESTAMPTZ DEFAULT now()     -- auto-managed timestamp
        );
        """)
        print("Table 'stock_profiles' created or already exists.")


        # Create a table for news analysis if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news_analysis (
            tic             VARCHAR(20) NOT NULL,              -- stock ticker
            url             TEXT NOT NULL,                    -- URL of the news article
            title           TEXT NOT NULL,                    -- Title of the news article
            content         TEXT,                             -- Content of the news article
            publisher       TEXT,                             -- Publisher of the news article
            published_at  TIMESTAMP NOT NULL,               -- Date and time the news was published
            category        VARCHAR(50),                      -- Category of the news (e.g., fundamental, technical)
            event_type      TEXT,                             -- Type of event described in the news
            time_horizon    INT,                      -- Time horizon of the impact (e.g., short_term)
            duration        TEXT,                             -- Duration of the impact
            impact_magnitude INT,                    -- Magnitude of the impact (e.g., minor, major)
            affected_dimensions TEXT[],                      -- List of affected dimensions (e.g., revenue, profit)
            sentiment       INT,                     -- Sentiment analysis result (e.g., positive, negative)
            raw_json_sha256 CHAR(64) NOT NULL,               -- hash of the raw JSON payload for integrity/lineage
            updated_at      TIMESTAMPTZ DEFAULT now(),
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
            token_count     INT NOT NULL,
            -- optional integrity/lineage
            chunk_sha256    TEXT NOT NULL,
            transcript_sha256 TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

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
            chunk_sha256    TEXT NOT NULL,
            transcript_sha256 TEXT NOT NULL,
                       
            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

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


        # Create a table for earnings transcript analysis if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcript_analysis (
            tic                     VARCHAR(10) NOT NULL,
            fiscal_year             INT NOT NULL,
            fiscal_quarter           INT NOT NULL,

            -- === Past analysis ===
            sentiment               SMALLINT,       -- -1, 0, 1
            durability              SMALLINT,       -- 0, 1, 2
            performance_factors     TEXT[] NOT NULL DEFAULT '{}',
            past_summary            TEXT,

            -- === Future analysis ===
            guidance_direction      SMALLINT,       -- -1, 0, 1
            revenue_outlook         SMALLINT,       -- -1, 0, 1
            margin_outlook          SMALLINT,       -- -1, 0, 1
            earnings_outlook        SMALLINT,       -- -1, 0, 1
            cashflow_outlook        SMALLINT,       -- -1, 0, 1
            growth_acceleration     SMALLINT,       -- -1, 0, 1
            future_outlook_sentiment SMALLINT,      -- -1, 0, 1
            catalysts               TEXT[] NOT NULL DEFAULT '{}',
            future_summary          TEXT,

            -- === Risk analysis ===
            risk_mentioned          SMALLINT,       -- 0 or 1
            risk_impact             SMALLINT,       -- -1, 0, 1
            risk_time_horizon       SMALLINT,       -- 0, 1, 2
            risk_factors            TEXT[] NOT NULL DEFAULT '{}',
            risk_summary            TEXT,

            -- === Mitigation / risk response ===
            mitigation_mentioned     SMALLINT,      -- 0 or 1
            mitigation_effectiveness SMALLINT,      -- -1, 0, 1
            mitigation_time_horizon  SMALLINT,      -- 0, 1, 2
            mitigation_actions       TEXT[] NOT NULL DEFAULT '{}',
            mitigation_summary       TEXT,

            -- Optional for tracking & versioning
            transcript_sha256      TEXT NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'earnings_transcript_analysis' created or already exists with composite primary key.")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_grades (
            tic             VARCHAR(10)        NOT NULL,
            url             TEXT               NOT NULL,
            published_at    TIMESTAMP          NOT NULL,
            broker          TEXT,
            grade           SMALLINT,                      -- +1 = Buy, 0 = Hold, -1 = Sell
            action          TEXT,                          -- upgrade, downgrade, initiation, reiteration, other
            raw_json_sha256 CHAR(64)          NOT NULL,               -- hash of the raw JSON payload for integrity/lineage  
            updated_at      TIMESTAMPTZ DEFAULT now(),
            
            PRIMARY KEY (tic, url)
        );
        """)
        print("Table 'analyst_grades' created or already exists.")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_rating_monthly_summary (
            tic               VARCHAR(10)   NOT NULL,
            start_date        DATE          NOT NULL,
            end_date          DATE          NOT NULL,

            -- ---- Price Target (pt_) statistics ----
            pt_count          INTEGER       DEFAULT 0,
            pt_high           FLOAT,
            pt_low            FLOAT,
            pt_p25            FLOAT,
            pt_median         FLOAT,
            pt_p75            FLOAT,
            pt_mean           FLOAT,
            pt_stddev         FLOAT,
            pt_dispersion     FLOAT,

            pt_upgrade_n      INTEGER       DEFAULT 0,
            pt_downgrade_n    INTEGER       DEFAULT 0,
            pt_reiterate_n    INTEGER       DEFAULT 0,
            pt_init_n         INTEGER       DEFAULT 0,

            -- ---- Grade statistics ----
            grade_count       INTEGER       DEFAULT 0,
            grade_buy_n       INTEGER       DEFAULT 0,
            grade_hold_n      INTEGER       DEFAULT 0,
            grade_sell_n      INTEGER       DEFAULT 0,
            grade_buy_ratio   FLOAT,
            grade_hold_ratio  FLOAT,
            grade_sell_ratio  FLOAT,
            grade_balance     FLOAT,

            grade_upgrade_n   INTEGER       DEFAULT 0,
            grade_downgrade_n INTEGER       DEFAULT 0,
            grade_reiterate_n INTEGER       DEFAULT 0,
            grade_init_n      INTEGER       DEFAULT 0,

            -- ---- Implied return statistics ----
            ret_mean          FLOAT,
            ret_median        FLOAT,
            ret_p25           FLOAT,
            ret_p75           FLOAT,
            ret_stddev        FLOAT,
            ret_dispersion    FLOAT,
            ret_high          FLOAT,
            ret_low           FLOAT,

            ret_upgrade_n     INTEGER       DEFAULT 0,
            ret_downgrade_n   INTEGER       DEFAULT 0,
            ret_reiterate_n   INTEGER       DEFAULT 0,
            ret_init_n        INTEGER       DEFAULT 0,

            -- ---- Price statistics ----
            price_start       FLOAT,
            price_end         FLOAT,
            price_high        FLOAT,
            price_low         FLOAT,
            price_p25         FLOAT,
            price_median      FLOAT,
            price_p75         FLOAT,
            price_mean        FLOAT,
            price_stddev      FLOAT,

            updated_at        TIMESTAMPTZ DEFAULT NOW(),

            PRIMARY KEY (tic, start_date, end_date)
        );
        """)
        print("Table 'analyst_rating_monthly_summary' created or already exists.")

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