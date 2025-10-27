import requests
import os
from psycopg import connect
from server.database.utils import connect_to_db
import json
from etl_pipeline.utils import hash_dict

# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/news/stock"


# Fetching news data
def fetch_news(tic, limit=100):
    source_url = f"{BASE_URL}?symbols={tic}&limit={limit}&apikey={API_KEY}"
    response = requests.get(source_url)
    if response.status_code == 200:
        return response.json(), source_url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

# Insert news data into the table
def insert_news(data, tic, source_url, conn):
    total_records = 0
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute(
                    """
                    INSERT INTO raw.news (
                        tic, url, source, raw_json, raw_json_sha256, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (tic, url) DO UPDATE
                    SET 
                        source = EXCLUDED.source,
                        raw_json = EXCLUDED.raw_json,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW();
                    """, (
                    tic,
                    record.get("url"),
                    record.get("source"),
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
            data, source_url = fetch_news(tic=tic, limit=100)
            if data:
                total_records += insert_news(data, tic, source_url, conn)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()