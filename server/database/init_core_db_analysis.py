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

        # Ensure the pgcrypto extension is available
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        print("Extension 'pgcrypto' created or already exists.")



        # Create a table for news analysis if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news_analysis (
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id           UUID NOT NULL,
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
            
            UNIQUE (tic, url),
            UNIQUE (event_id),
            FOREIGN KEY (event_id)
                REFERENCES core.news (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'news_analysis' created or already exists with composite primary key.")



        # Create a table for earnings transcript chunks if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcript_chunks (
            -- Transcript identity
            tic             VARCHAR(10) NOT NULL,
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,
                       
            -- Sequential id within a single transcript (1..N)
            event_id         UUID NOT NULL,
            chunk_id        INT NOT NULL,

            -- Chunk content
            chunk           TEXT NOT NULL,
            token_count     INT NOT NULL,
            -- optional integrity/lineage
            chunk_sha256    CHAR(64)  NOT NULL,
            transcript_sha256 CHAR(64)  NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            -- Keys
            PRIMARY KEY (event_id, chunk_id),

            -- business convenience uniqueness if you address chunks via (tic, y, q, chunk_id)
            UNIQUE (tic, calendar_year, calendar_quarter, chunk_id),

            -- Enforce parent relationship
            FOREIGN KEY (event_id)
                REFERENCES core.earnings_transcripts (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'earnings_transcript_chunks' created or already exists with unique constraint.")

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
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,

            -- Sequential id within a single transcript (1..N)
            event_id         UUID NOT NULL,
            chunk_id        INT NOT NULL,
            chunk_sha256    CHAR(64)  NOT NULL,
            transcript_sha256 CHAR(64) NOT NULL,
                       
            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (event_id, chunk_id),
                       
            -- business convenience uniqueness if you address chunks via (tic, y, q, chunk_id)
            UNIQUE (tic, calendar_year, calendar_quarter, chunk_id),
                                  
            FOREIGN KEY (event_id)
                REFERENCES core.earnings_transcripts (event_id)
                ON DELETE CASCADE,


            FOREIGN KEY (event_id, chunk_id)
                REFERENCES core.earnings_transcript_chunks (event_id, chunk_id)
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
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id           UUID NOT NULL,
            tic                     VARCHAR(10) NOT NULL,
            calendar_year           SMALLINT     NOT NULL,
            calendar_quarter        SMALLINT    NOT NULL,

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
            growth_drivers               TEXT[] NOT NULL DEFAULT '{}',
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
            transcript_sha256     CHAR(64) NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, calendar_year, calendar_quarter),
            UNIQUE (event_id),
            FOREIGN KEY (event_id)
                REFERENCES core.earnings_transcripts (event_id)
                ON DELETE CASCADE
            
        );
        """)
        print("Table 'earnings_transcript_analysis' created or already exists with unique constraint.")



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