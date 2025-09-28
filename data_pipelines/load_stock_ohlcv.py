import yfinance as yf
import psycopg as pg
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
    try:
        cursor = conn.cursor()
        for ticker, df in data.items():
            rows = [
                (row['Date'], ticker, row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
                for _, row in df.iterrows()
            ]
            query = """
            INSERT INTO stock_ohlcv (date, tic, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, tic) DO NOTHING;
            """
            cursor.executemany(query, rows)  # Use executemany for bulk insert
        conn.commit()
        print("Data inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM stock_metadata;")
        records = cursor.fetchall()
        for tic in records:
            stock_data = fetch_stock_data(tic[0])
            insert_stock_data(conn, stock_data)
        conn.close()