import requests
import os
from psycopg import connect
from server.database.utils import connect_to_db
import json
from etl_pipeline.utils import hash_dict


# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/balance-sheet-statement"


# Fetching data
def fetch_records(tic, period, limit=5):
    url = f"{BASE_URL}?symbol={tic}&limit={limit}&period={period}"
    response = requests.get(url + f"&apikey={API_KEY}")
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

# Insert data into the table
def insert_records(data, tic, url, conn):
    total_records = 0
    try:
        with conn.cursor() as cur:
            for record in data:
                fiscal_year = int(record.get("fiscalYear"))
                fiscal_quarter = int(record.get("period")[1]) if record.get("period") != "FY" else 0
                cur.execute("""
                    INSERT INTO raw.balance_sheets (
                        tic, fiscal_year, fiscal_quarter, source, 
                        raw_json, raw_json_sha256, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (tic, fiscal_year, fiscal_quarter) 
                    DO UPDATE
                    SET source = EXCLUDED.source,
                        raw_json = EXCLUDED.raw_json,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW()
                    WHERE raw.balance_sheets.raw_json_sha256 IS DISTINCT FROM EXCLUDED.raw_json_sha256;
                """, (
                    tic,
                    fiscal_year,
                    fiscal_quarter,
                    url,
                    json.dumps(record),  # raw JSON payload
                    hash_dict(record)
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
        cursor.execute("SELECT tic FROM core.stock_profiles;")
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