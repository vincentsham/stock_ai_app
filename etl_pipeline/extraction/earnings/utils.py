import json
from etl_pipeline.utils import hash_dict, hash_text


# Insert earnings transcript data into the database
def insert_record(conn, data, tic, earnings_date, url):
    total_records = 0
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings_transcripts (
            tic, earnings_date, source, 
            transcript_sha256,
            raw_json, raw_json_sha256
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, earnings_date)
        DO UPDATE SET
            source = EXCLUDED.source,
            transcript_sha256 = EXCLUDED.transcript_sha256,
            raw_json = EXCLUDED.raw_json,
            raw_json_sha256 = EXCLUDED.raw_json_sha256,
            updated_at = NOW()
        WHERE
            raw.earnings_transcripts.transcript_sha256 <>EXCLUDED.transcript_sha256;
        """

        cursor.execute(query, (
            tic,
            earnings_date,
            # data.get("transcript"),  # transcript text
            # hash_text(data.get("transcript")),  # SHA-256 hash of the transcript
            url,
            hash_text(data.get("transcript")),
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