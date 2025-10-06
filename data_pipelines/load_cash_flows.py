import requests
import os
from psycopg import connect
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database credentials
DB_NAME = os.getenv("PGNAME")
DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")

# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/cash-flow-statement"

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

# Fetching data
def fetch_records(tic, period, limit=5):
    url = f"{BASE_URL}?symbol={tic}&limit={limit}&period={period}"
    response = requests.get(url + f"&apikey={API_KEY}")
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

# Insert data into thetable
def insert_records(data, tic, url, conn):
    total_records = 0
    try:
        with conn.cursor() as cur:
            for record in data:
                fiscal_year = int(record.get("fiscalYear"))
                fiscal_quarter = int(record.get("period")[1]) if record.get("period") != "FY" else 0
                cur.execute("""
                    INSERT INTO raw.cash_flows (
                        tic, fiscal_year, fiscal_quarter, fiscal_date, raw_json, source
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tic, fiscal_year, fiscal_quarter) DO UPDATE
                    SET fiscal_date = EXCLUDED.fiscal_date,
                        raw_json = EXCLUDED.raw_json,
                        source = EXCLUDED.source;
                """, (
                    tic,
                    fiscal_year,
                    fiscal_quarter,
                    record.get("date"),
                    json.dumps(record),  # raw JSON payload
                    url
                ))
                total_records += cur.rowcount
            conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting or updating data for ticker {tic}: {e}")
        conn.rollback()
        return 0

# Main function
def main():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM stock_metadata;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            total_records = 0
            for period in ["Q1", "Q2", "Q3", "Q4", "FY"]:
                data, url = fetch_records(tic=tic, period=period, limit=5)
                if data:
                    total_records += insert_records(data, tic, url, conn)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()