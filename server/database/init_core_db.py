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
            tic             VARCHAR(10) NOT NULL,              -- stock ticker
            url             TEXT NOT NULL,                    -- URL of the news article
            title           TEXT NOT NULL,                    -- Title of the news article
            content         TEXT,                             -- Content of the news article
            publisher       TEXT,                             -- Publisher of the news article
            published_at  TIMESTAMP NOT NULL,               -- Date and time the news was published
            category        VARCHAR(50),                      -- Category of the news (e.g., fundamental, technical)
            event_type      TEXT,                             -- Type of event described in the news
            time_horizon    SMALLINT,                      -- Time horizon of the impact (e.g., short_term)
            duration        TEXT,                             -- Duration of the impact
            impact_magnitude SMALLINT,                    -- Magnitude of the impact (e.g., minor, major)
            affected_dimensions TEXT[],                      -- List of affected dimensions (e.g., revenue, profit)
            sentiment       SMALLINT,                     -- Sentiment analysis result (e.g., positive, negative)
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
            tic             VARCHAR(10) NOT NULL,
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
            tic             VARCHAR(10) NOT NULL,
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_metrics (
            -- Entity & period
            tic               VARCHAR(10) NOT NULL,
            fiscal_year       INT         NOT NULL,
            fiscal_quarter    SMALLINT    NOT NULL CHECK (fiscal_quarter BETWEEN 1 AND 4),

            -- Raw values / estimates
            eps               FLOAT,
            eps_estimated     FLOAT,
            eps_ttm           FLOAT,
            revenue           FLOAT,
            revenue_estimated FLOAT,
            revenue_ttm       FLOAT,
                       
            pre_eps_flag     SMALLINT,
            pre_revenue_flag SMALLINT,
                       

            -- EPS phase
            eps_phase         VARCHAR(50),

            -- EPS surprise / beats
            eps_surprise_pct               FLOAT,
            eps_beat_flag                  SMALLINT,
            eps_beat_count_4q              SMALLINT,
            eps_beat_streak_length         SMALLINT,
            eps_consistency                FLOAT,

            -- EPS growth / trend / acceleration
            eps_qoq_growth_pct             FLOAT,
            eps_growth_flag                SMALLINT,
            eps_growth_count_4q            SMALLINT,
            eps_growth_streak_length       SMALLINT,
            eps_yoy_growth_pct             FLOAT,
            eps_trend_strength             FLOAT,
            eps_ttm_growth_pct             FLOAT,
            eps_acceleration               FLOAT,
            eps_ttm_acceleration           FLOAT,
            eps_acceleration_flag          SMALLINT,
            eps_acceleration_count_4q      SMALLINT,
            eps_acceleration_streak_length SMALLINT,

            -- Revenue surprise / beats
            revenue_surprise_pct               FLOAT,
            revenue_beat_flag                  SMALLINT,
            revenue_beat_count_4q              SMALLINT,
            revenue_beat_streak_length         SMALLINT,
            revenue_consistency                FLOAT,

            -- Revenue growth / trend / acceleration
            revenue_qoq_growth_pct             FLOAT,
            revenue_growth_flag                SMALLINT,
            revenue_growth_count_4q            SMALLINT,
            revenue_growth_streak_length       SMALLINT,
            revenue_yoy_growth_pct             FLOAT,
            revenue_trend_strength             FLOAT,
            revenue_ttm_growth_pct             FLOAT,
            revenue_acceleration               FLOAT,
            revenue_ttm_acceleration           FLOAT,
            revenue_acceleration_flag          SMALLINT,
            revenue_acceleration_count_4q      SMALLINT,
            revenue_acceleration_streak_length SMALLINT,

            -- Bookkeeping
            updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'earnings_metrics' created or already exists.")

       # Create a table for income statements if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.income_statements (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            fiscal_year                           SMALLINT     NOT NULL,
            fiscal_quarter                        SMALLINT,                 -- 1–4 if quarterly; NULL if FY
            period                                VARCHAR(10)  NOT NULL,    -- "Q1".."Q4", "FY" (as reported)
            earnings_date                          DATE         NOT NULL,    -- period end date (company fiscal)

            -- Filing / meta
            filing_date                           DATE,
            accepted_date                         TIMESTAMP,                -- raw feed is naive (no TZ)
            cik                                   VARCHAR(20),
            reported_currency                     VARCHAR(10),

            -- Key financials (from JSON; snake_cased)
            revenue                               BIGINT,
            cost_of_revenue                       BIGINT,
            gross_profit                          BIGINT,
            research_and_development_expenses     BIGINT,
            general_and_administrative_expenses   BIGINT,
            selling_and_marketing_expenses        BIGINT,
            selling_general_and_administrative_expenses BIGINT,
            other_expenses                        BIGINT,
            operating_expenses                    BIGINT,
            cost_and_expenses                     BIGINT,

            -- Operating & non-operating
            ebitda                                BIGINT,
            ebit                                  BIGINT,
            non_operating_income_excluding_interest BIGINT,
            operating_income                      BIGINT,
            total_other_income_expenses_net       BIGINT,
            income_before_tax                     BIGINT,
            income_tax_expense                    BIGINT,

            -- Net income breakdowns
            net_income_from_continuing_operations BIGINT,
            net_income_from_discontinued_operations BIGINT,
            other_adjustments_to_net_income       BIGINT,
            net_income                            BIGINT,
            net_income_deductions                 BIGINT,
            bottom_line_net_income                BIGINT,

            -- Interest details
            net_interest_income                   BIGINT,
            interest_income                       BIGINT,
            interest_expense                      BIGINT,
            depreciation_and_amortization         BIGINT,

            -- EPS & shares
            eps                                   NUMERIC(10,2),
            eps_diluted                           NUMERIC(10,2),
            weighted_average_shs_out              BIGINT,
            weighted_average_shs_out_dil          BIGINT,

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'income_statements' created or already exists with composite primary key.")




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