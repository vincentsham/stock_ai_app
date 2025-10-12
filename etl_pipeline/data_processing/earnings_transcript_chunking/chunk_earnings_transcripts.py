from server.database.utils import connect_to_db
import hashlib
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
            # Fetch records from raw.earnings_transcripts
            cursor.execute("""
                SELECT tic, fiscal_year, fiscal_quarter, earnings_date, transcript, transcript_hash
                FROM raw.earnings_transcripts
                WHERE transcript IS NOT NULL;
            """)
            records = cursor.fetchall()
            total_records = 0
            for record in records:
                tic = record[0]
                fiscal_year = record[1]
                fiscal_quarter = record[2]
                earnings_date = record[3]
                transcript = record[4]
                transcript_hash = record[5]
                
                chunks = chunk_text(transcript, max_tokens=512, overlap_tokens=512//10)
                
                # Chunk the transcript
                for chunk_id, chunk in enumerate(chunks):
                    chunk_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()


                    # Insert chunk into core.earnings_transcript_chunks
                    cursor.execute("""
                        INSERT INTO core.earnings_transcript_chunks (
                            tic, fiscal_year, fiscal_quarter, earnings_date, chunk_id, chunk, token_count, chunk_hash, transcript_hash
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tic, fiscal_year, fiscal_quarter, chunk_id) DO NOTHING;
                    """, (
                        tic, fiscal_year, fiscal_quarter, earnings_date, chunk_id, chunk, len(enc.encode(chunk)), chunk_hash, transcript_hash
                    ))
                    total_records += cursor.rowcount

            conn.commit()
            print("Chunks processed and loaded successfully.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

if __name__ == "__main__":
    process_and_load_chunks()