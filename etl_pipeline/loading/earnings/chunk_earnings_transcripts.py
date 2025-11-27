from database.utils import connect_to_db
from etl_pipeline.utils import hash_dict, hash_text
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter


enc = tiktoken.get_encoding("cl100k_base")

# Function to chunk text
def tok_len(s: str) -> int:
    return len(enc.encode(s))

def chunk_text(text, max_tokens=512, overlap_tokens=50):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            r"(?<=\n)\s*",     # split after newlines
            r"(?<=\.)\s+",     # split after a period
            r" ",              # fallback word-level
            r""                # fallback char-level
        ],
        is_separator_regex=True,
        chunk_size=max_tokens,
        chunk_overlap=overlap_tokens,
        length_function=tok_len,
        keep_separator=True,
    )

    chunks = []
    dialogues = text.split('\n')
    for dialogue in dialogues:
        if dialogue.strip():
            if ": " not in dialogue:
                speaker, content = "Unknown", dialogue
            else:
                speaker, content = dialogue.split(": ", 1)

            splits = text_splitter.split_text(content)
            for i, chunk in enumerate(splits):
                prefix = f"{speaker}: "
                if i > 0:
                    prefix += "(contd) "
                chunks.append(prefix + chunk.strip())

    return chunks



# Main function to process and load chunks
def process_and_load_chunks():
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            # Fetch records from core.earnings_transcripts
            cursor.execute("""
                SELECT et.event_id, et.tic, et.calendar_year, et.calendar_quarter, 
                       et.earnings_date, et.transcript, et.transcript_sha256
                FROM core.earnings_transcripts AS et
                LEFT JOIN core.earnings_transcript_chunks AS etc
                ON et.tic = etc.tic
                    AND et.calendar_year = etc.calendar_year
                    AND et.calendar_quarter = etc.calendar_quarter
                WHERE et.transcript IS NOT NULL
                    AND (etc.transcript_sha256 IS NULL
                        OR et.transcript_sha256 <> etc.transcript_sha256);
            """)
            records = cursor.fetchall()
            total_records = 0
            for record in records:
                event_id = record[0]
                tic = record[1]
                calendar_year = record[2]
                calendar_quarter = record[3]
                earnings_date = record[4]
                transcript = record[5]
                transcript_hash = record[6]

                chunks = chunk_text(transcript, max_tokens=512, overlap_tokens=512//10)
                
                # Chunk the transcript
                for chunk_id, chunk in enumerate(chunks):
                    chunk_hash = hash_text(chunk)


                    # Insert chunk into core.earnings_transcript_chunks
                    cursor.execute("""
                        INSERT INTO core.earnings_transcript_chunks (
                            event_id, tic, calendar_year, calendar_quarter,
                            chunk_id, chunk, token_count, chunk_sha256, transcript_sha256, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (tic, calendar_year, calendar_quarter, chunk_id) 
                        DO UPDATE SET
                            event_id = EXCLUDED.event_id,
                            chunk = EXCLUDED.chunk,
                            token_count = EXCLUDED.token_count,
                            chunk_sha256 = EXCLUDED.chunk_sha256,
                            transcript_sha256 = EXCLUDED.transcript_sha256,
                            updated_at = NOW()
                        WHERE core.earnings_transcript_chunks.transcript_sha256 <> EXCLUDED.transcript_sha256
                            OR core.earnings_transcript_chunks.chunk_sha256 <> EXCLUDED.chunk_sha256;
                    """, (
                        event_id, tic, calendar_year, calendar_quarter, 
                        chunk_id, chunk, len(enc.encode(chunk)), chunk_hash, transcript_hash
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