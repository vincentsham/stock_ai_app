import yfinance as yf
import psycopg as pg
from server.database.utils import connect_to_db
import pandas as pd

# Fetch stock data from yfinance
def fetch_records(tic, start_date=None):
    data = {}
    print(f"Fetching data for {tic}...")
    stock = yf.Ticker(tic)
    if start_date:
        hist = stock.history(start=start_date, end=None)
    else:
        hist = stock.history(period="max")  # Fetch all available historical data
    data[tic] = hist.reset_index()
    return data


# Check if tic exists in raw.stock_ohlcv table
def check_tic_exists(conn, tic):
    try:
        cursor = conn.cursor()
        query = "SELECT 1 FROM raw.stock_ohlcv WHERE tic = %s LIMIT 1;"
        cursor.execute(query, (tic,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking tic existence: {e}")
        return False

# Check if the most recent record close price changed too much compared to the new data with the same date
def check_price_change(conn, tic, new_data):
    try:
        # print(new_data)
        cursor = conn.cursor()
        query = "SELECT close FROM raw.stock_ohlcv WHERE tic = %s AND date = %s;"
        cursor.execute(query, (tic, new_data['Date'].iloc[-1]))
        result = cursor.fetchone()
        if result:
            last_close = result[0]
            new_close = new_data['Close'].iloc[-1]
            # Check if the price change is greater than a certain threshold (e.g., 5%)
            if abs(float(new_close) - float(last_close)) / float(last_close) > 0.1:
                print(f"Price change for {tic} is significant: {last_close} -> {new_close}")
                return True
        return False
    except Exception as e:
        print(f"Error checking price change: {e}")
        return False    

# Insert stock data into the database
def insert_records(conn, data):
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
                volume = EXCLUDED.volume,
                updated_at = NOW();
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
        cursor.execute("SELECT date FROM raw.stock_ohlcv ORDER BY date DESC LIMIT 1;")
        last_date = cursor.fetchone()[0] if cursor.rowcount > 0 else pd.to_datetime("2000-01-01")
        print(f"Last date in database: {last_date}")
        # last_date minus 30 days
        last_date = last_date - pd.Timedelta(days=30)

        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()


        for tic in records:
            stock_data = fetch_records(tic[0], start_date=last_date)
            # Check if tic exists in the database
            if check_tic_exists(conn, tic[0]):
                # Check if the most recent record close price changed too much compared to the new data with the same date
                if check_price_change(conn, tic[0], stock_data[tic[0]]):
                    print(f"Significant price change detected for {tic[0]}, fetching all historical data.")
                    stock_data = fetch_records(tic[0], start_date=None)
            else:
                print(f"{tic[0]} does not exist in the database, fetching all historical data.")
                stock_data = fetch_records(tic[0], start_date=None)
            total_records = insert_records(conn, stock_data)
            print(f"For {tic[0]}: Total records processed = {total_records}")
        conn.close()