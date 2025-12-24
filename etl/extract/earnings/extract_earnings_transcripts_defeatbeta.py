from database.utils import connect_to_db
from etl.utils import hash_dict, hash_text, filter_complete_years, get_calendar_year_quarter
from defeatbeta_api.data.ticker import Ticker
import pandas as pd
import json
from database.utils import insert_records, insert_record


def extract_all_earnings_transcripts(tic, num_transcripts=None):
    transcripts_list = []
    ticker = Ticker(tic)
    earning_call_transcripts = ticker.earning_call_transcripts()
    transcripts_df = earning_call_transcripts.get_transcripts_list()
    transcripts_df = transcripts_df.sort_values(by='report_date', ascending=False)
    transcripts_df = transcripts_df.head(num_transcripts) if num_transcripts else transcripts_df
    for _, row in transcripts_df.iterrows():
        transcript_text = [row['transcripts'][i]['speaker'] + ": " + row['transcripts'][i]['content'] for i in range(len(row['transcripts']))]
        transcript_text = "\n".join(transcript_text)

        transcript_data = {
            "ticker": tic.upper(),
            "year": row['fiscal_year'],
            "quarter": f"Q{row['fiscal_quarter']}",
            "date": row['report_date'],
            "transcript": transcript_text,
            "url": 'https://github.com/defeat-beta/defeatbeta-api',  # Placeholder URL as defeatbeta does not provide direct URLs,
            "source": "defeatbeta"
        }
        transcripts_list.append(transcript_data)
    return transcripts_list
    

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        tics = cursor.fetchall()
        tics = [tic[0] for tic in tics]
        # tics = [tic[0] if tic[0] not in ['NVDA', 'AAPL', 'TSLA'] else None for tic in tics]

        for tic in tics:
            if tic is None:
                continue
            total_records = 0
            transcripts = extract_all_earnings_transcripts(tic, num_transcripts=None)
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

            total_inserted = insert_records(conn, df_transcripts, "raw.earnings_transcripts", ["tic", "calendar_year", "calendar_quarter"], where=["raw_json_sha256"])
            print(f"For {tic}: Total records processed = {total_inserted}")  
            # for i in range(df_transcripts.shape[0]):
            #     df_row = df_transcripts.iloc[i:i+1]
            #     # Change dtype to object for single row insertion
            #     df_row = df_row.astype(object)
            #     total_inserted = insert_record(conn, df_row, "raw.earnings_transcripts", ["tic", "calendar_year", "calendar_quarter"], where=["raw_json_sha256"])
            #     if total_inserted > 0:
            #         total_records += total_inserted
            #         print(df_row)
            # print(f"For {tic}: Total records processed = {total_records}")  
        conn.close()
