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