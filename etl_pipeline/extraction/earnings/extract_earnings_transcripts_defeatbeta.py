from database.utils import connect_to_db
from etl_pipeline.utils import hash_dict, hash_text
from defeatbeta_api.data.ticker import Ticker
from utils import insert_record, lookup_record


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
            "url": 'https://github.com/defeat-beta/defeatbeta-api'  # Placeholder URL as defeatbeta does not provide direct URLs,
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
            for transcript in transcripts:
                earnings_date = transcript.get("date")
                earnings_date = lookup_record(conn, tic, earnings_date)
                url = transcript.get("url")
                if earnings_date:
                    total_records += insert_record(conn, transcript, tic, earnings_date, url)
            print(f"For {tic}: Total records processed = {total_records}")  
        conn.close()
