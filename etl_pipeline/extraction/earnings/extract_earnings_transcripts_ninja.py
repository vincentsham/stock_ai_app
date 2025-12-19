import requests
from database.utils import connect_to_db
import os
import datetime
import time
import json
from etl_pipeline.utils import hash_dict, hash_text
from utils import insert_record, lookup_record


# Load environment variables
NINJA_API_KEY = os.getenv("NINJA_API_KEY")


# Fetch earnings transcript data from the API
def fetch_record(ticker, year, quarter):
    url = f"https://api.api-ninjas.com/v1/earningstranscript?ticker={ticker}&year={year}&quarter={quarter}"
    headers = {"X-Api-Key": NINJA_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return None, None


if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()

        for record in records:
            tic = record[0]
            total_records = 0
            for year in range(2025, 2027):
                for quarter in range(1, 5):
                    data, url = fetch_record(tic, year, quarter)
                    if data:
                        earnings_date = data.get("date")
                        earnings_date = lookup_record(conn, tic, earnings_date)
                        total_records += insert_record(conn, data, tic, earnings_date, url)
                    else:
                        print(f"No data found for {tic} for Q{quarter} {year}")
            print(f"For {tic}: Total records processed = {total_records}")  
        conn.close()

