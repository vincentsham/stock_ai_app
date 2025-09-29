import yfinance as yf
from psycopg import connect
from psycopg.errors import UniqueViolation
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to PostgreSQL
def connect_to_db():
    try:
        conn = connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Fetch stock metadata from yfinance
def fetch_stock_metadata(tickers):
    data = []
    for ticker in tickers:
        print(f"Fetching metadata for {ticker}...")
        stock = yf.Ticker(ticker)
        info = stock.info
        exchange = info.get("exchange")
        if exchange == "NMS":
            exchange = "NASDAQ"
        data.append((
            ticker,
            info.get("longName"),
            info.get("sector"),
            info.get("industry"),
            info.get("country"),
            info.get("marketCap"),
            info.get("fullTimeEmployees"),
            info.get("longBusinessSummary"),
            info.get("website"),
            exchange,
            info.get("currency"),
        ))
    return data

# Insert stock metadata into the database
def insert_stock_metadata(conn, data):
    total_records = 0
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO stock_metadata (tic, name, sector, industry, country, market_cap, employees, description, website, exchange, currency)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tic) DO UPDATE SET
            name = EXCLUDED.name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            country = EXCLUDED.country,
            market_cap = EXCLUDED.market_cap,
            employees = EXCLUDED.employees,
            description = EXCLUDED.description,
            website = EXCLUDED.website,
            exchange = EXCLUDED.exchange,
            currency = EXCLUDED.currency,
            last_updated = CURRENT_TIMESTAMP;
        """
        for record in data:
            try:
                cursor.execute(query, record)
                total_records += cursor.rowcount
            except UniqueViolation:
                print(f"Duplicate entry for {record[0]}")
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting metadata: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "NVDA"]
    conn = connect_to_db()
    if conn:
        stock_metadata = fetch_stock_metadata(tickers)
        total_records = insert_stock_metadata(conn, stock_metadata)
        print(f"Total records inserted: {total_records}")
        conn.close()