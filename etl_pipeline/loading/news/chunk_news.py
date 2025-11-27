from database.utils import connect_to_db
from etl_pipeline.utils import hash_dict, hash_text
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter


enc = tiktoken.get_encoding("cl100k_base")

# Function to chunk text
def tok_len(s: str) -> int:
    return len(enc.encode(s))



# Main function to process and load chunks
def process_and_load_chunks():
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            # Fetch records from core.earnings_transcripts
            cursor.execute("""
                SELECT n.event_id, n.tic, n.published_at, n.url, n.title, n.content, n.raw_json_sha256
                FROM core.news AS n
                LEFT JOIN core.news_chunks AS nc
                ON n.event_id = nc.event_id
                WHERE n.url IS NOT NULL
                    AND (nc.raw_json_sha256 IS NULL
                        OR n.raw_json_sha256 <> nc.raw_json_sha256);
            """)
            records = cursor.fetchall()
            total_records = 0
            for record in records:
                event_id = record[0]
                tic = record[1]
                published_at = record[2]
                url = record[3]
                title = record[4]
                content = record[5]
                raw_json_sha256 = record[6]

                chunk = title + " - " + content
                chunk_hash = hash_text(chunk)

                # Insert chunk into core.news_chunks
                cursor.execute("""
                    INSERT INTO core.news_chunks (
                        event_id, tic, published_at, url, chunk_id,
                        chunk, token_count, chunk_sha256, raw_json_sha256, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (tic, url, chunk_id) 
                    DO UPDATE SET
                        event_id = EXCLUDED.event_id,
                        published_at = EXCLUDED.published_at,
                        chunk_id = EXCLUDED.chunk_id,
                        chunk = EXCLUDED.chunk,
                        token_count = EXCLUDED.token_count,
                        chunk_sha256 = EXCLUDED.chunk_sha256,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW()
                    WHERE core.news_chunks.raw_json_sha256 <> EXCLUDED.raw_json_sha256
                        OR core.news_chunks.chunk_sha256 <> EXCLUDED.chunk_sha256;
                """, (
                    event_id, tic, published_at, url, 0,
                    chunk, len(enc.encode(chunk)), chunk_hash, raw_json_sha256
                ))
                total_records += cursor.rowcount

            conn.commit()
            return total_records

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    total_records = process_and_load_chunks()
    print(f"Chunks processed and loaded successfully. Total new/updated chunks: {total_records}")