import yfinance as yf
import psycopg as pg
from server.database.utils import connect_to_db
import os

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