import os
from database.utils import connect_to_db
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
import database.config

# Initialize the embedding model
embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL")
embedding_model = OpenAIEmbeddings(model=embedding_model_name)

# Main function to process and store embeddings
def process_and_store_embeddings():
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            # Fetch chunks without embeddings
            cursor.execute("""
                SELECT etc.chunk_id, etc.event_id, etc.chunk_no, etc.tic, 
                       etc.calendar_year, etc.calendar_quarter,
                       etc.chunk, etc.chunk_sha256, etc.transcript_sha256
                FROM core.earnings_transcript_chunks AS etc
                LEFT JOIN core.earnings_transcript_embeddings AS e
                ON etc.chunk_id = e.chunk_id
                WHERE e.chunk_sha256 IS NULL
                    OR e.chunk_sha256 <> etc.chunk_sha256
                    OR e.transcript_sha256 IS NULL
                    OR e.transcript_sha256 <> etc.transcript_sha256;
            """)
            records = cursor.fetchall()

            # Define batch size
            batch_size = 32

            # Add tqdm progress bar
            total_records = 0
            for i in tqdm(range(0, len(records), batch_size), desc="Processing batches"):
                batch = records[i:i + batch_size]

                # Prepare batch chunks for embedding
                chunk_texts = [record[6] for record in batch]

                # Generate embeddings for the batch
                embeddings = embedding_model.embed_documents(chunk_texts)

                for record, embedding in zip(batch, embeddings):
                    chunk_id = record[0]
                    event_id = record[1]
                    chunk_no = record[2]
                    tic = record[3]
                    calendar_year = record[4]
                    calendar_quarter = record[5]
                    chunk_hash = record[7]
                    transcript_hash = record[8]

                    # Insert embedding into the database
                    cursor.execute("""
                        INSERT INTO core.earnings_transcript_embeddings (
                            chunk_id, event_id, chunk_no, tic, 
                            calendar_year, calendar_quarter, 
                            chunk_sha256, transcript_sha256, 
                            embedding, embedding_model, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET
                            event_id = EXCLUDED.event_id,
                            chunk_no = EXCLUDED.chunk_no,
                            chunk_sha256 = EXCLUDED.chunk_sha256,
                            transcript_sha256 = EXCLUDED.transcript_sha256,
                            embedding = EXCLUDED.embedding,
                            embedding_model = EXCLUDED.embedding_model,
                            updated_at = NOW()
                        WHERE core.earnings_transcript_embeddings.transcript_sha256 <> EXCLUDED.transcript_sha256
                            OR core.earnings_transcript_embeddings.chunk_sha256 <> EXCLUDED.chunk_sha256;
                    """, (
                        chunk_id, event_id, chunk_no, tic, calendar_year, calendar_quarter,
                        chunk_hash, transcript_hash, embedding, embedding_model_name
                    ))
                    total_records += cursor.rowcount

            conn.commit()
            return total_records

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    total_records = process_and_store_embeddings()
    print(f"Total records processed: {total_records}")