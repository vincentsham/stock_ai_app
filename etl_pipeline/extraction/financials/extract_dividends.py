import requests
import os
from psycopg import connect
from database.utils import connect_to_db
import json
from etl_pipeline.utils import hash_dict
import pandas as pd

# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/dividends"


# Fetching data
def fetch_records(tic, limit=100):
    url = f"{BASE_URL}?symbol={tic}&limit={limit}"
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
                # Map API fields to DB columns
                try:
                    cur.execute("""
                        INSERT INTO raw.dividends (
                            tic, ex_dividend_date, declaration_date, payment_date,
                            adj_dividend, dividend, dividend_yield, frequency, 
                            source, raw_json, raw_json_sha256, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                        )
                        ON CONFLICT (tic, ex_dividend_date) DO UPDATE SET
                            declaration_date = EXCLUDED.declaration_date,
                            payment_date = EXCLUDED.payment_date,
                            adj_dividend = EXCLUDED.adj_dividend,
                            dividend = EXCLUDED.dividend,
                            dividend_yield = EXCLUDED.dividend_yield,
                            frequency = EXCLUDED.frequency,
                            source = EXCLUDED.source,
                            raw_json = EXCLUDED.raw_json,
                            raw_json_sha256 = EXCLUDED.raw_json_sha256,
                            updated_at = NOW()
                        WHERE raw.dividends.raw_json_sha256 <> EXCLUDED.raw_json_sha256;
                    """,
                    (
                        tic,
                        pd.to_datetime(record.get("date")),
                        pd.to_datetime(record.get("declarationDate")) if record.get("declarationDate") else None,
                        pd.to_datetime(record.get("paymentDate")) if record.get("paymentDate") else None,
                        record.get("adjDividend"),
                        record.get("dividend"),
                        record.get("yield"),
                        record.get("frequency"),
                        url,
                        json.dumps(record),
                        hash_dict(record)
                    ))

                except Exception as e:
                    print(f"Error inserting record for {tic} on {record.get('date')}: {e}")
                    print("Record data:", (
                        tic,
                        pd.to_datetime(record.get("date")),
                        record.get("declarationDate"),  
                        pd.to_datetime(record.get("declarationDate")),
                        pd.to_datetime(record.get("paymentDate")),
                        record.get("adjDividend"),
                        record.get("dividend"),
                        record.get("yield"),
                        record.get("frequency"),
                        url)
                    )
                    raise e  # Re-raise the exception after logging
                total_records += cur.rowcount
            conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting or updating dividends: {e}")
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
            # You can page through results if needed
            data, url = fetch_records(tic=tic, limit=100)
            if data:
                total_records += insert_records(data, tic, url,conn)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()