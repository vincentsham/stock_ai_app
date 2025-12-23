import requests
import os
from psycopg import connect
from database.utils import connect_to_db
import json
from etl_pipeline.utils import hash_dict
import pandas as pd
from database.utils import insert_records

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
            df = {}
            data, source_url = fetch_news(tic=tic, limit=500)
            if data:
                df['tic'] = tic
                df['url'] = [item.get('url') for item in data]
                df['source'] = 'fmp'
                df['raw_json'] = [json.dumps(record) for record in data]
                df['raw_json_sha256'] = [hash_dict(record) for record in data]
                df = pd.DataFrame(df)
                total_records = insert_records(conn, df, "raw.news", keys=['tic', 'url'])
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()