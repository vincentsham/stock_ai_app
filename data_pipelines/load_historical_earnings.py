import requests
from psycopg import connect
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
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

# Fetch historical earnings data
def fetch_historical_earnings(ticker, exchange):
    url = f"https://coincodex.com/api/v1/stocks/get_historical/earnings?symbol={exchange}:{ticker}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return []

# Insert historical earnings data into the database
def insert_historical_earnings(conn, data, ticker):
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings (
            tic, fiscal_year, fiscal_quarter, fiscal_date, earnings_date, eps, eps_estimated, session, revenue, revenue_estimated, price_before, price_after, last_updated
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, fiscal_year, fiscal_quarter)
        DO UPDATE SET
            fiscal_date = EXCLUDED.fiscal_date,
            earnings_date = EXCLUDED.earnings_date,
            eps = EXCLUDED.eps,
            eps_estimated = EXCLUDED.eps_estimated,
            session = EXCLUDED.session,
            revenue = EXCLUDED.revenue,
            revenue_estimated = EXCLUDED.revenue_estimated,
            price_before = EXCLUDED.price_before,
            price_after = EXCLUDED.price_after,
            last_updated = EXCLUDED.last_updated;
        """
        total_records = 0
        for record in data:
            fiscal_date = record.get("fiscalDateEnding")
            fiscal_date = pd.to_datetime(fiscal_date) 

            fiscal_year = fiscal_date.year
            fiscal_month = fiscal_date.month
            if fiscal_month in [3, 4, 5]:
                fiscal_quarter = 1
            elif fiscal_month in [6, 7, 8]:
                fiscal_quarter = 2
            elif fiscal_month in [9, 10, 11]:
                fiscal_quarter = 3
            elif fiscal_month in [12]:
                fiscal_quarter = 4
            elif fiscal_month in [1, 2]:
                fiscal_quarter = 4
                fiscal_year -= 1
            else:
                print(f"Unexpected fiscal date {fiscal_date} for ticker {ticker}")
                continue

            cursor.execute(query, (
                ticker,
                fiscal_year,
                fiscal_quarter,
                record.get("fiscalDateEnding"),
                record.get("date"),
                record.get("eps") if pd.notnull(record.get("eps")) else None,
                record.get("epsEstimated") if pd.notnull(record.get("epsEstimated")) else None,
                record.get("time") if pd.notnull(record.get("time")) else None,
                int(float(record.get("revenue", 0) or 0)) if pd.notnull(record.get("revenue")) else None,
                int(float(record.get("revenueEstimated", 0) or 0)) if pd.notnull(record.get("revenueEstimated")) else None,
                record.get("priceBefore") if pd.notnull(record.get("priceBefore")) else None,
                record.get("priceAfter") if pd.notnull(record.get("priceAfter")) else None,
                record.get("updatedFromDate")
            ))
            total_records += cursor.rowcount
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting data for {ticker}: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic, exchange FROM stock_metadata;")
        records = cursor.fetchall()
        for tic, exchange in records:
            data = fetch_historical_earnings(tic, exchange)
            total_records = insert_historical_earnings(conn, data, tic)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()
