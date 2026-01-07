import requests
from database.utils import connect_to_db
import os
import datetime
import time
import json
from etl.utils import hash_dict, hash_text, filter_complete_years, get_calendar_year_quarter
import pandas as pd
from database.utils import insert_records, insert_record


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
            transcripts = []
            for year in range(2025, 2027):
                for quarter in range(1, 5):
                    data, url = fetch_record(tic, year, quarter)
                    if data:
                        data['source'] = "api-ninjas"
                        transcripts.append(data)
                    else:
                        print(f"No data found for {tic} for Q{quarter} {year}")
            
            transcripts_list = []
            for transcript in transcripts:
                earnings_date = transcript.get("date")
                source = transcript.get("source")
                url = transcript.get("url")
                transcripts_list.append({
                    "tic": tic.upper(),
                    "earnings_date": earnings_date,
                    "url": url,
                    "transcript_sha256": hash_text(transcript.get("transcript")),
                    "raw_json": json.dumps(transcript),
                    "raw_json_sha256": hash_dict(transcript),
                    "source": source
                })
            df_transcripts = pd.DataFrame(transcripts_list)
            df_transcripts['earnings_date'] = pd.to_datetime(df_transcripts['earnings_date'])
            df_transcripts = df_transcripts.sort_values(by='earnings_date', ascending=False)
            df_transcripts = filter_complete_years(df_transcripts, tic)
            calendar_year, calendar_quarter = zip(*[get_calendar_year_quarter(date) for date in df_transcripts['earnings_date']])
            df_transcripts.loc[:, 'calendar_year'] = calendar_year
            df_transcripts.loc[:, 'calendar_quarter'] = calendar_quarter


            total_inserted = insert_record(conn, df_transcripts, "raw.earnings_transcripts", ["tic", "calendar_year", "calendar_quarter"], where=["raw_json_sha256"])
            print(f"For {tic}: Total records processed = {total_inserted}")  
        conn.close()
