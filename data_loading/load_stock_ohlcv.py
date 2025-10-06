import yfinance as yf
import psycopg as pg
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database credentials
DB_NAME = os.getenv("PGNAME")
DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")

# Connect to PostgreSQL
def connect_to_db():
    try:
        conn = pg.connect(
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

# Fetch stock data from yfinance
def fetch_stock_data(tic):
    data = {}
    print(f"Fetching all available historical data for {tic}...")
    stock = yf.Ticker(tic)
    hist = stock.history(period="max")  # Fetch all available historical data
    data[tic] = hist.reset_index()
    return data

# Insert stock data into the database
def insert_stock_data(conn, data):
    total_records = 0
    try:
        cursor = conn.cursor()
        for ticker, df in data.items():
            rows = [
                (row['Date'], ticker, row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
                for _, row in df.iterrows()
            ]
            query = """
            INSERT INTO raw.stock_ohlcv (date, tic, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, tic) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            """
            cursor.executemany(query, rows)  # Use executemany for bulk insert
            total_records += cursor.rowcount
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM stock_metadata;")
        records = cursor.fetchall()
        for tic in records:
            stock_data = fetch_stock_data(tic[0])
            total_records = insert_stock_data(conn, stock_data)
            print(f"For {tic[0]}: Total records processed = {total_records}") 
        conn.close()