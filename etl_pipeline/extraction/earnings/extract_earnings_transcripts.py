import requests
from psycopg import connect
from database.utils import connect_to_db
import os
import datetime
import time
import json
from etl_pipeline.utils import hash_dict, hash_text


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
        return None

# Insert earnings transcript data into the database
def insert_record(conn, data, tic, earnings_date, url=None):
    total_records = 0
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings_transcripts (
            tic, earnings_date, source, 
            raw_json, raw_json_sha256
        ) VALUES (
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, earnings_date)
        DO UPDATE SET
            source = EXCLUDED.source,
            raw_json = EXCLUDED.raw_json,
            raw_json_sha256 = EXCLUDED.raw_json_sha256,
            updated_at = NOW()
        WHERE
            raw.earnings_transcripts.raw_json_sha256 <>EXCLUDED.raw_json_sha256;
        """
        cursor.execute(query, (
            tic,
            earnings_date,
            # data.get("transcript"),  # transcript text
            # hash_text(data.get("transcript")),  # SHA-256 hash of the transcript
            url,
            json.dumps(data),  # Serialize the raw_json field
            hash_dict(data),  # Compute SHA-256 hash of the entire payload
        ))
        total_records += cursor.rowcount
        conn.commit()

        # Calculate total records (inserted + updated)
        return total_records

    except Exception as e:
        print(f"Error inserting transcript for {tic}: {e}")
        conn.rollback()
        return 0



def lookup_record(conn, tic, earnings_date):
    try:
        cursor = conn.cursor()
        query = """
        SELECT earnings_date
        FROM raw.earnings
        WHERE tic = %s AND ABS(earnings_date::DATE - %s::DATE) <= 10;
        """
        cursor.execute(query, (tic, earnings_date))
        result = cursor.fetchone()
        if result:
            print(f"Found fiscal data for {tic} near {earnings_date}:= {result[0]}")
            return result[0]
        else:
            print(f"Found no fiscal data for {tic} near {earnings_date}")
            return None
    except Exception as e:
        print(f"Error fetching fiscal data for {tic} near {earnings_date}: {e}")
        return None

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

