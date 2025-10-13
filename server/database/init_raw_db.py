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

        # Create a table for stock profiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.stock_profiles (
            tic            VARCHAR(10) PRIMARY KEY,
            name           VARCHAR(255),
            sector         VARCHAR(255),
            industry       VARCHAR(255),
            country        VARCHAR(255),
            market_cap     BIGINT,
            employees      INTEGER,
            description    TEXT,
            website        TEXT,
            exchange       TEXT,
            currency       VARCHAR(10),
            source         TEXT,
            raw_json       JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at    TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'stock_profiles' created or already exists.")


        # Create a table for stock OHLCV data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.stock_ohlcv (
            date          DATE NOT NULL,
            tic           VARCHAR(10) NOT NULL,
            open          NUMERIC(12,4) NOT NULL,
            high          NUMERIC(12,4) NOT NULL,
            low           NUMERIC(12,4) NOT NULL,
            close         NUMERIC(12,4) NOT NULL,
            volume        BIGINT NOT NULL,
            updated_at   TIMESTAMPTZ DEFAULT now(),
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
            fiscal_date DATE,              
            earnings_date DATE NOT NULL,
            session VARCHAR(10),
            eps NUMERIC(10,4),
            eps_estimated NUMERIC(10,4),
            revenue NUMERIC(20,2),
            revenue_estimated NUMERIC(20,2),
            price_before NUMERIC(12,4),
            price_after NUMERIC(12,4),
            source                 TEXT,                  -- e.g., 'fmp', 'yahoo', etc.
            raw_json               JSONB        NOT NULL,                 -- verbatim payload (optional but useful)
            raw_json_sha256        CHAR(64)     NOT NULL,
            updated_at            TIMESTAMPTZ DEFAULT now(),
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
            transcript      TEXT         NOT NULL,
            transcript_sha256 CHAR(64)     NOT NULL,
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
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
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
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
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
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
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
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
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (tic, url)             -- composite PK: unique news per ticker+url
        );
        """)
        print("Table 'news' created or already exists with composite primary key.")


        # Create a table for analyst price targets data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.analyst_price_targets (
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            news_title        text,
            news_base_url     text,
            news_publisher    text,
                       
            analyst_name      text,
            broker            text,
            price_target      numeric(12,2),
            adj_price_target  numeric(12,2),
            price_when_posted numeric(12,4),

            url               text NOT NULL,
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (tic, url)
        );
        """)
        print("Table 'analyst_price_targets' created or already exists with composite primary key.")

        # Create a table for analyst grades data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.analyst_grades (
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            news_title        text,
            news_base_url     text,
            news_publisher    text,

            new_grade         text,
            previous_grade    text,
            grading_company   text,
            action            text,
            price_when_posted numeric(12,4),

            url               text NOT NULL,
            source          TEXT,
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (tic, url)
        );
        """)
        print("Table 'analyst_grades' created or already exists with composite primary key.")



    
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