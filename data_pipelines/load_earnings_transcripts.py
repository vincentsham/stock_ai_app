import requests
from psycopg import connect
from dotenv import load_dotenv
import os
import datetime
import time
import json


# Load environment variables
load_dotenv()

# Database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
NINJA_API_KEY = os.getenv("NINJA_API_KEY")

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
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO earnings_transcripts (
            raw_json, fiscal_quarter, last_updated, earnings_date, fiscal_year, transcript, tic, source
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, fiscal_year, fiscal_quarter)
        DO UPDATE SET
            raw_json = EXCLUDED.raw_json,
            last_updated = EXCLUDED.last_updated,
            earnings_date = EXCLUDED.earnings_date,
            transcript = EXCLUDED.transcript,
            source = EXCLUDED.source
        WHERE earnings_transcripts.last_updated IS NULL OR EXCLUDED.last_updated > earnings_transcripts.last_updated;
        """
        cursor.execute(query, (
            json.dumps(data),  # Serialize the raw_json field
            fiscal_quarter,
            datetime.datetime.now(),
            earnings_date,
            fiscal_year,
            data.get("transcript"),
            tic,
            url
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()

# Update fiscal year and quarter in earnings_transcripts table
def update_fiscal_data_record_by_record(conn):
    try:
        cursor = conn.cursor()
        select_query = """
        SELECT tic, earnings_date FROM earnings_transcripts;
        """
        cursor.execute(select_query)
        records = cursor.fetchall()

        for record in records:
            tic, earnings_date = record
            update_query = """
            UPDATE earnings_transcripts
            SET 
                fiscal_year = earnings.fiscal_year,
                fiscal_quarter = earnings.fiscal_quarter
            FROM 
                earnings
            WHERE 
                earnings_transcripts.tic = earnings.tic
            AND 
                earnings_transcripts.earnings_date = earnings.earnings_date
            AND 
                earnings_transcripts.tic = %s
            AND 
                earnings_transcripts.earnings_date = %s;
            """
            cursor.execute(update_query, (tic, earnings_date))
        conn.commit()
        print("Updated fiscal_year and fiscal_quarter for each record in earnings_transcripts table.")
    except Exception as e:
        print(f"Error updating fiscal data record by record: {e}")
        conn.rollback()

# Update fiscal year and quarter for a specific record before inserting earnings transcript
def update_fiscal_data_before_insert(conn, tic, earnings_date):
    try:
        cursor = conn.cursor()
        update_query = """
        UPDATE earnings_transcripts
        SET 
            fiscal_year = earnings.fiscal_year,
            fiscal_quarter = earnings.fiscal_quarter
        FROM 
            earnings
        WHERE 
            earnings_transcripts.tic = earnings.tic
        AND 
            earnings_transcripts.earnings_date = earnings.earnings_date
        AND 
            earnings_transcripts.tic = %s
        AND 
            earnings_transcripts.earnings_date = %s;
        """
        cursor.execute(update_query, (tic, earnings_date))
        conn.commit()
    except Exception as e:
        print(f"Error updating fiscal data for {tic} on {earnings_date}: {e}")
        conn.rollback()


def lookup_fiscal_data(conn, tic, earnings_date):
    try:
        cursor = conn.cursor()
        query = """
        SELECT fiscal_year, fiscal_quarter, earnings_date
        FROM earnings
        WHERE tic = %s AND ABS(earnings_date::DATE - %s::DATE) <= 10;
        """
        cursor.execute(query, (tic, earnings_date))
        result = cursor.fetchone()
        if result:
            print(f"Found fiscal data for {tic} near {earnings_date}: FY{result[0]} Q{result[1]} on {result[2]}")
            return result[0], result[1], result[2]  # fiscal_year, fiscal_quarter, earnings_date
        else:
            return None, None, None
    except Exception as e:
        print(f"Error fetching fiscal data for {tic} near {earnings_date}: {e}")
        return None, None, None

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM stock_metadata;")
        records = cursor.fetchall()

        for record in records:
            tic = record[0]
            for year in range(2025, 2027):
                for quarter in range(1, 5):
                    data, url = fetch_earnings_transcript(tic, year, quarter)
                    if data:
                        earnings_date = data.get("date")
                        fiscal_year, fiscal_quarter, earnings_date = lookup_fiscal_data(conn, tic, earnings_date)
                        insert_earnings_transcript(conn, data, tic, fiscal_year, fiscal_quarter, earnings_date, url)
                        print(f"Inserted transcript for {tic} for Q{fiscal_quarter} {fiscal_year}")
                    else:
                        print(f"No data found for {tic} for Q{quarter} {year}")
        conn.close()

