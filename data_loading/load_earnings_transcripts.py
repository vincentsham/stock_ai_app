import requests
from psycopg import connect
from server.database.utils import connect_to_db
import os
import datetime
import time
import json
import hashlib

# Load environment variables
NINJA_API_KEY = os.getenv("NINJA_API_KEY")


# Fetch earnings transcript data from the API
def fetch_earnings_transcript(ticker, year, quarter):
    url = f"https://api.api-ninjas.com/v1/earningstranscript?ticker={ticker}&year={year}&quarter={quarter}"
    headers = {"X-Api-Key": NINJA_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return None

# Insert earnings transcript data into the database
def insert_earnings_transcript(conn, data, tic, fiscal_year, fiscal_quarter, earnings_date, url=None):
    total_records = 0
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings_transcripts (
            tic, fiscal_year, fiscal_quarter, earnings_date, transcript, transcript_hash, raw_json, source
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, fiscal_year, fiscal_quarter)
        DO UPDATE SET
            earnings_date = EXCLUDED.earnings_date,
            raw_json = EXCLUDED.raw_json,
            source = EXCLUDED.source;
        """
        cursor.execute(query, (
            tic,
            fiscal_year,
            fiscal_quarter,
            earnings_date,
            data.get("transcript"),  # transcript text
            hashlib.sha256(data.get("transcript", "").encode('utf-8')).hexdigest(),  # transcript_hash
            json.dumps(data),  # Serialize the raw_json field    
            url
        ))
        total_records += cursor.rowcount
        conn.commit()

        # Calculate total records (inserted + updated)
        return total_records

    except Exception as e:
        print(f"Error inserting transcript for {tic}: {e}")
        conn.rollback()
        return 0



def lookup_fiscal_data(conn, tic, earnings_date):
    try:
        cursor = conn.cursor()
        query = """
        SELECT fiscal_year, fiscal_quarter, earnings_date
        FROM raw.earnings
        WHERE tic = %s AND ABS(earnings_date::DATE - %s::DATE) <= 10;
        """
        cursor.execute(query, (tic, earnings_date))
        result = cursor.fetchone()
        if result:
            print(f"Found fiscal data for {tic} near {earnings_date}: FY{result[0]} Q{result[1]} on {result[2]}")
            return result[0], result[1], result[2]  # fiscal_year, fiscal_quarter, earnings_date
        else:
            print(f"Found no fiscal data for {tic} near {earnings_date}")
            return None, None, None
    except Exception as e:
        print(f"Error fetching fiscal data for {tic} near {earnings_date}: {e}")
        return None, None, None

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM raw.stock_metadata;")
        records = cursor.fetchall()

        for record in records:
            tic = record[0]
            total_records = 0
            for year in range(2025, 2027):
                for quarter in range(1, 5):
                    data, url = fetch_earnings_transcript(tic, year, quarter)
                    if data:
                        earnings_date = data.get("date")
                        fiscal_year, fiscal_quarter, earnings_date = lookup_fiscal_data(conn, tic, earnings_date)
                        if not fiscal_year or not fiscal_quarter:
                            continue
                        total_records += insert_earnings_transcript(conn, data, tic, fiscal_year, fiscal_quarter, earnings_date, url)
                        print(f"Inserted transcript for {tic} for Q{fiscal_quarter} {fiscal_year}")
                    else:
                        print(f"No data found for {tic} for Q{quarter} {year}")
            print(f"For {tic}: Total records processed = {total_records}")  
        conn.close()

