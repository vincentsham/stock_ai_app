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

        # Ensure the vector extension is available
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("Extension 'vector' created or already exists.")
        



        # # Create a table for news chunks if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.news_chunks (
        #     chunk_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        #     -- News article identity
        #     tic             VARCHAR(10) NOT NULL,
        #     published_at    TIMESTAMP   NOT NULL,  
        #     url             TEXT NOT NULL,
                       
        #     event_id        UUID NOT NULL,
        #     chunk_no        INT NOT NULL,

        #     -- Chunk content
        #     chunk           TEXT NOT NULL,
        #     token_count     INT NOT NULL,

        #     chunk_sha256    CHAR(64)  NOT NULL,
        #     raw_json_sha256 CHAR(64)  NOT NULL,

        #     updated_at      TIMESTAMPTZ DEFAULT now(),

        #     -- Keys
        #     UNIQUE (event_id, chunk_no),
        #     UNIQUE (tic, url, chunk_no),

        #     -- Enforce parent relationship
        #     FOREIGN KEY (event_id)
        #         REFERENCES core.news (event_id)
        #         ON DELETE CASCADE
        # );
        # """)
        # print("Table 'news_chunks' created or already exists with unique constraint.")

        # # Create a full-text index for keyword/BM25 search
        # cursor.execute("""
        # CREATE INDEX IF NOT EXISTS idx_core_news_chunks_tsv
        #   ON core.news_chunks
        #   USING GIN (to_tsvector('english', chunk));
        # """)
        # print("Index 'idx_core_news_chunks_tsv' created or already exists.")



        # # Create a table for news embeddings if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.news_embeddings (
        #     chunk_id        UUID NOT NULL,

        #     tic             VARCHAR(10) NOT NULL,
        #     published_at    TIMESTAMP   NOT NULL,  
        #     url             TEXT NOT NULL,

        #     event_id        UUID NOT NULL,
        #     chunk_no        INT NOT NULL,
        #     chunk_sha256    CHAR(64)  NOT NULL,
        #     raw_json_sha256 CHAR(64) NOT NULL,
                       
        #     -- Embedding vector
        #     embedding       VECTOR(1536) NOT NULL,
        #     embedding_model TEXT NOT NULL,

        #     updated_at      TIMESTAMPTZ DEFAULT now(),

        #     PRIMARY KEY (chunk_id),

        #     UNIQUE (event_id, chunk_no),
        #     UNIQUE (tic, url, chunk_no),

        #     FOREIGN KEY (event_id)
        #         REFERENCES core.news (event_id)
        #         ON DELETE CASCADE,
        #     FOREIGN KEY (chunk_id)
        #         REFERENCES core.news_chunks (chunk_id)
        #         ON DELETE CASCADE
        # );
        # """)
        # print("Table 'news_embeddings' created or already exists with composite primary key.")

        # # Create an HNSW index for the embeddings
        # cursor.execute("""
        # CREATE INDEX IF NOT EXISTS idx_core_news_embeddings_vec_hnsw
        #   ON core.news_embeddings
        #   USING hnsw (embedding vector_cosine_ops)
        #   WITH (m = 16, ef_construction = 200);
        # """)
        # print("Index 'idx_core_news_embeddings_vec_hnsw' created or already exists.")

        # # Create a table for news analysis if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.news_analysis (
        #     inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     event_id           UUID NOT NULL,
        #     tic             VARCHAR(10) NOT NULL,              -- stock ticker
        #     url             TEXT NOT NULL,                    -- URL of the news article
        #     title           TEXT NOT NULL,                    -- Title of the news article
        #     content         TEXT,                             -- Content of the news article
        #     publisher       TEXT,                             -- Publisher of the news article
        #     published_at  TIMESTAMP NOT NULL,               -- Date and time the news was published
        #     category        VARCHAR(50),                      -- Category of the news (e.g., fundamental, technical)
        #     event_type      TEXT,                             -- Type of event described in the news
        #     time_horizon    SMALLINT,                      -- Time horizon of the impact (e.g., short_term)
        #     duration        TEXT,                             -- Duration of the impact
        #     magnitude SMALLINT,                    -- Magnitude of the impact (e.g., minor, major)
        #     affected_dimensions TEXT[],                      -- List of affected dimensions (e.g., revenue, profit)
        #     sentiment       SMALLINT,                     -- Sentiment analysis result (e.g., positive, negative)
        #     raw_json_sha256 CHAR(64) NOT NULL,               -- hash of the raw JSON payload for integrity/lineage
        #     updated_at      TIMESTAMPTZ DEFAULT now(),
            
        #     UNIQUE (tic, url),
        #     UNIQUE (event_id),
        #     FOREIGN KEY (event_id)
        #         REFERENCES core.news (event_id)
        #         ON DELETE CASCADE
        # );
        # """)
        # print("Table 'news_analysis' created or already exists with composite primary key.")



        # # Create a table for earnings transcript chunks if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.earnings_transcript_chunks (
        #     chunk_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        #     -- Transcript identity
        #     tic             VARCHAR(10) NOT NULL,
        #     calendar_year   SMALLINT     NOT NULL,
        #     calendar_quarter SMALLINT    NOT NULL,
                       
        #     -- Sequential id within a single transcript (1..N)
        #     event_id        UUID NOT NULL,
        #     chunk_no        INT NOT NULL,

        #     -- Chunk content
        #     chunk           TEXT NOT NULL,
        #     token_count     INT NOT NULL,
        #     -- optional integrity/lineage
        #     chunk_sha256    CHAR(64)  NOT NULL,
        #     transcript_sha256 CHAR(64)  NOT NULL,

        #     updated_at      TIMESTAMPTZ DEFAULT now(),

        #     -- Keys
        #     UNIQUE (event_id, chunk_no),
        #     UNIQUE (tic, calendar_year, calendar_quarter, chunk_no),

        #     -- Enforce parent relationship
        #     FOREIGN KEY (event_id)
        #         REFERENCES core.earnings_transcripts (event_id)
        #         ON DELETE CASCADE
        # );
        # """)
        # print("Table 'earnings_transcript_chunks' created or already exists with unique constraint.")

        # # Create a full-text index for keyword/BM25 search
        # cursor.execute("""
        # CREATE INDEX IF NOT EXISTS idx_core_earnings_transcripts_chunks_tsv
        #   ON core.earnings_transcript_chunks
        #   USING GIN (to_tsvector('english', chunk));
        # """)
        # print("Index 'idx_core_earnings_transcripts_chunks_tsv' created or already exists.")



        # # Create a table for earnings transcript embeddings if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.earnings_transcript_embeddings (
        #     chunk_id        UUID NOT NULL,

        #     tic             VARCHAR(10) NOT NULL,
        #     calendar_year   SMALLINT     NOT NULL,
        #     calendar_quarter SMALLINT    NOT NULL,

        #     event_id        UUID NOT NULL,
        #     chunk_no        INT NOT NULL,
        #     chunk_sha256    CHAR(64)  NOT NULL,
        #     transcript_sha256 CHAR(64) NOT NULL,
                       
        #     -- Embedding vector
        #     embedding       VECTOR(1536) NOT NULL,
        #     embedding_model TEXT NOT NULL,

        #     updated_at      TIMESTAMPTZ DEFAULT now(),

        #     PRIMARY KEY (chunk_id),
                       
        #     UNIQUE (event_id, chunk_no),
        #     UNIQUE (tic, calendar_year, calendar_quarter, chunk_no),
                                  
        #     FOREIGN KEY (event_id)
        #         REFERENCES core.earnings_transcripts (event_id)
        #         ON DELETE CASCADE,

        #     FOREIGN KEY (chunk_id)
        #         REFERENCES core.earnings_transcript_chunks (chunk_id)
        #         ON DELETE CASCADE
        # );
        # """)
        # print("Table 'earnings_transcript_embeddings' created or already exists with composite primary key.")

        # # Create an HNSW index for the embeddings
        # cursor.execute("""
        # CREATE INDEX IF NOT EXISTS idx_core_earnings_transcript_embeddings_vec_hnsw
        #   ON core.earnings_transcript_embeddings
        #   USING hnsw (embedding vector_cosine_ops)
        #   WITH (m = 16, ef_construction = 200);
        # """)
        # print("Index 'idx_core_earnings_transcript_embeddings_vec_hnsw' created or already exists.")



        # # Create a table for earnings transcript analysis if it does not exist
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS core.earnings_transcript_analysis (
        #     inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     event_id           UUID NOT NULL,
        #     tic                     VARCHAR(10) NOT NULL,
        #     calendar_year           SMALLINT     NOT NULL,
        #     calendar_quarter        SMALLINT    NOT NULL,

        #     -- === Past analysis ===
        #     sentiment               SMALLINT,       -- -1, 0, 1
        #     durability              SMALLINT,       -- 0, 1, 2
        #     performance_factors     TEXT[] NOT NULL DEFAULT '{}',
        #     past_summary            TEXT,

        #     -- === Future analysis ===
        #     guidance_direction      SMALLINT,       -- -1, 0, 1
        #     revenue_outlook         SMALLINT,       -- -1, 0, 1
        #     margin_outlook          SMALLINT,       -- -1, 0, 1
        #     earnings_outlook        SMALLINT,       -- -1, 0, 1
        #     cashflow_outlook        SMALLINT,       -- -1, 0, 1
        #     growth_acceleration     SMALLINT,       -- -1, 0, 1
        #     future_outlook_sentiment SMALLINT,      -- -1, 0, 1
        #     growth_drivers               TEXT[] NOT NULL DEFAULT '{}',
        #     future_summary          TEXT,

        #     -- === Risk analysis ===
        #     risk_mentioned          SMALLINT,       -- 0 or 1
        #     risk_impact             SMALLINT,       -- -1, 0, 1
        #     risk_time_horizon       SMALLINT,       -- 0, 1, 2
        #     risk_factors            TEXT[] NOT NULL DEFAULT '{}',
        #     risk_summary            TEXT,

        #     -- === Mitigation / risk response ===
        #     mitigation_mentioned     SMALLINT,      -- 0 or 1
        #     mitigation_effectiveness SMALLINT,      -- -1, 0, 1
        #     mitigation_time_horizon  SMALLINT,      -- 0, 1, 2
        #     mitigation_actions       TEXT[] NOT NULL DEFAULT '{}',
        #     mitigation_summary       TEXT,

        #     -- Optional for tracking & versioning
        #     transcript_sha256     CHAR(64) NOT NULL,
        #     updated_at      TIMESTAMPTZ DEFAULT now(),

        #     UNIQUE (tic, calendar_year, calendar_quarter),
        #     UNIQUE (event_id),
        #     FOREIGN KEY (event_id)
        #         REFERENCES core.earnings_transcripts (event_id)
        #         ON DELETE CASCADE
            
        # );
        # """)
        # print("Table 'earnings_transcript_analysis' created or already exists with unique constraint.")


        # Create a table for news chunks if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news_chunks (
            chunk_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- News article identity
            tic             VARCHAR(10) NOT NULL,
            published_at    TIMESTAMP   NOT NULL,  
            url             TEXT NOT NULL,
                       
            event_id        UUID NOT NULL,
            chunk_no        INT NOT NULL,

            -- Chunk content
            chunk           TEXT NOT NULL,
            token_count     INT NOT NULL,

            chunk_sha256    CHAR(64)  NOT NULL,
            raw_json_sha256 CHAR(64)  NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            -- Keys
            UNIQUE (event_id, chunk_no),
            UNIQUE (tic, url, chunk_no),

            -- Enforce parent relationship
            FOREIGN KEY (event_id)
                REFERENCES core.news (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'news_chunks' created or already exists with unique constraint.")

        # Create a full-text index for keyword/BM25 search
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_core_news_chunks_tsv
          ON core.news_chunks
          USING GIN (to_tsvector('english', chunk));
        """)
        print("Index 'idx_core_news_chunks_tsv' created or already exists.")



        # Create a table for news embeddings if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news_embeddings (
            chunk_id        UUID NOT NULL,

            tic             VARCHAR(10) NOT NULL,
            published_at    TIMESTAMP   NOT NULL,  
            url             TEXT NOT NULL,

            event_id        UUID NOT NULL,
            chunk_no        INT NOT NULL,
            chunk_sha256    CHAR(64)  NOT NULL,
            raw_json_sha256 CHAR(64) NOT NULL,
                       
            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (chunk_id),

            UNIQUE (event_id, chunk_no),
            UNIQUE (tic, url, chunk_no),

            FOREIGN KEY (event_id)
                REFERENCES core.news (event_id)
                ON DELETE CASCADE,
            FOREIGN KEY (chunk_id)
                REFERENCES core.news_chunks (chunk_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'news_embeddings' created or already exists with composite primary key.")

        # Create an HNSW index for the embeddings
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_core_news_embeddings_vec_hnsw
          ON core.news_embeddings
          USING hnsw (embedding vector_cosine_ops)
          WITH (m = 16, ef_construction = 200);
        """)
        print("Index 'idx_core_news_embeddings_vec_hnsw' created or already exists.")

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
            magnitude SMALLINT,                    -- Magnitude of the impact (e.g., minor, major)
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
            chunk_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Transcript identity
            tic             VARCHAR(10) NOT NULL,
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,
                       
            -- Sequential id within a single transcript (1..N)
            event_id        UUID NOT NULL,
            chunk_no        INT NOT NULL,

            -- Chunk content
            chunk           TEXT NOT NULL,
            token_count     INT NOT NULL,
            -- optional integrity/lineage
            chunk_sha256    CHAR(64)  NOT NULL,
            transcript_sha256 CHAR(64)  NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            -- Keys
            UNIQUE (event_id, chunk_no),
            UNIQUE (tic, calendar_year, calendar_quarter, chunk_no),

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



        # Create a table for earnings transcript embeddings if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcript_embeddings (
            chunk_id        UUID NOT NULL,

            tic             VARCHAR(10) NOT NULL,
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,

            event_id        UUID NOT NULL,
            chunk_no        INT NOT NULL,
            chunk_sha256    CHAR(64)  NOT NULL,
            transcript_sha256 CHAR(64) NOT NULL,
                       
            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (chunk_id),
                       
            UNIQUE (event_id, chunk_no),
            UNIQUE (tic, calendar_year, calendar_quarter, chunk_no),
                                  
            FOREIGN KEY (event_id)
                REFERENCES core.earnings_transcripts (event_id)
                ON DELETE CASCADE,

            FOREIGN KEY (chunk_id)
                REFERENCES core.earnings_transcript_chunks (chunk_id)
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




        # Create a table for catalyst master if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.catalyst_master (
            catalyst_id      UUID PRIMARY KEY,
            tic              VARCHAR(10),
            date             DATE,
            catalyst_type    VARCHAR(64),
            title            TEXT,
            summary          TEXT,
            sentiment        SMALLINT,
            time_horizon     SMALLINT,
            magnitude        SMALLINT,
            impact_area      VARCHAR(32),

            mention_count    INTEGER DEFAULT 0,
            chunk_ids        TEXT[] DEFAULT '{}',
            citations         TEXT[] DEFAULT '{}',
            created_at       TIMESTAMPTZ DEFAULT now(),
            updated_at       TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'catalyst_master' created or already exists.")


        # Create a table for catalyst versions if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.catalyst_versions (
            catalyst_id      UUID NOT NULL,
            tic              VARCHAR(10),
            date             DATE,
            catalyst_type    VARCHAR(64),
            title            TEXT,
            summary          TEXT,
            sentiment        SMALLINT,
            time_horizon     SMALLINT,
            magnitude        SMALLINT,
            impact_area      VARCHAR(32),

            mention_count    INTEGER DEFAULT 0,
            chunk_ids        TEXT[] DEFAULT '{}',
            citations         TEXT[] DEFAULT '{}',
            version_no       INTEGER NOT NULL DEFAULT 0,
            updated_at       TIMESTAMPTZ DEFAULT now(),
            
            PRIMARY KEY (catalyst_id, version_no)
        );
        """)
        print("Table 'catalyst_versions' created or already exists.")


        # Trigger: auto-increment version_no on catalyst_versions INSERT
        cursor.execute("""
        CREATE OR REPLACE FUNCTION core.fn_auto_version_no()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.version_no := COALESCE(
                (SELECT MAX(version_no) FROM core.catalyst_versions
                 WHERE catalyst_id = NEW.catalyst_id), -1
            ) + 1;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
        DROP TRIGGER IF EXISTS trg_auto_version_no ON core.catalyst_versions;
        CREATE TRIGGER trg_auto_version_no
            BEFORE INSERT ON core.catalyst_versions
            FOR EACH ROW
            EXECUTE FUNCTION core.fn_auto_version_no();
        """)
        print("Trigger 'trg_auto_version_no' created on 'catalyst_versions'.")


        # Trigger: auto-upsert catalyst_master from catalyst_versions INSERT
        cursor.execute("""
        CREATE OR REPLACE FUNCTION core.fn_upsert_catalyst_master()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO core.catalyst_master (
                catalyst_id, tic, date, catalyst_type, title, summary,
                sentiment, time_horizon, magnitude, impact_area,
                mention_count, chunk_ids, citations, created_at, updated_at
            ) VALUES (
                NEW.catalyst_id, NEW.tic, NEW.date, NEW.catalyst_type,
                NEW.title, NEW.summary, NEW.sentiment,
                NEW.time_horizon, NEW.magnitude, NEW.impact_area,
                NEW.mention_count, NEW.chunk_ids, NEW.citations,
                now(), now()
            )
            ON CONFLICT (catalyst_id) DO UPDATE SET
                date          = EXCLUDED.date,
                catalyst_type = EXCLUDED.catalyst_type,
                title         = EXCLUDED.title,
                summary       = EXCLUDED.summary,
                sentiment     = EXCLUDED.sentiment,
                time_horizon  = EXCLUDED.time_horizon,
                magnitude     = EXCLUDED.magnitude,
                impact_area   = EXCLUDED.impact_area,
                mention_count = EXCLUDED.mention_count,
                chunk_ids     = EXCLUDED.chunk_ids,
                citations     = EXCLUDED.citations,
                updated_at    = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
        DROP TRIGGER IF EXISTS trg_upsert_catalyst_master ON core.catalyst_versions;
        CREATE TRIGGER trg_upsert_catalyst_master
            AFTER INSERT ON core.catalyst_versions
            FOR EACH ROW
            EXECUTE FUNCTION core.fn_upsert_catalyst_master();
        """)
        print("Trigger 'trg_upsert_catalyst_master' created on 'catalyst_versions'.")



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