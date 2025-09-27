from dotenv import load_dotenv
import os
from psycopg import connect
import getpass

# Load environment variables from .env file
load_dotenv()

# Database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Prompt for the postgres superuser password
def get_postgres_password():
    return getpass.getpass(prompt="Enter the postgres superuser password: ")


# Connect to PostgreSQL
try:
    conn = connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()


    # Test the connection by executing a simple query
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    if result and result[0] == 1:
        print("Connection test successful!")
    else:
        print("Connection test failed!")

  
    # Create a table for stock OHLCV data if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_ohlcv (
        date DATE NOT NULL,
        tic VARCHAR(10) NOT NULL,
        open FLOAT NOT NULL,
        high FLOAT NOT NULL,
        low FLOAT NOT NULL,
        close FLOAT NOT NULL,
        volume BIGINT NOT NULL,
        PRIMARY KEY (date, tic)
    );
    """)
    print("Table 'stock_ohlcv' created or already exists.")

    # Create a table for stock metadata if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_metadata (
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

    # Create a table for historical earnings data if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_earnings (
        tic VARCHAR(20) NOT NULL,
        fiscal_year INT NOT NULL,
        fiscal_quarter INT NOT NULL,
        fiscal_date_ending DATE,
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
    print("Table 'historical_earnings' created or already exists with composite primary key.")

    conn.commit()
    print("Tables created successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()