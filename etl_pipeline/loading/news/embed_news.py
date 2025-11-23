import os
from database.utils import connect_to_db
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm



# Load environment variables
load_dotenv()

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
                SELECT nc.event_id, nc.chunk_id, nc.tic, nc.published_at, nc.url,
                       nc.chunk, nc.chunk_sha256, nc.raw_json_sha256
                FROM core.news_chunks AS nc
                LEFT JOIN core.news_embeddings AS e
                ON nc.tic = e.tic
                    AND nc.url = e.url
                WHERE e.chunk_sha256 IS NULL
                    OR e.chunk_sha256 <> nc.chunk_sha256
                    OR e.raw_json_sha256 IS NULL
                    OR e.raw_json_sha256 <> nc.raw_json_sha256;
            """)
            records = cursor.fetchall()

            # Define batch size
            batch_size = 32

            # Add tqdm progress bar
            total_records = 0
            for i in tqdm(range(0, len(records), batch_size), desc="Processing batches"):
                batch = records[i:i + batch_size]

                # Prepare batch chunks for embedding
                chunk_texts = [record[5] for record in batch]

                # Generate embeddings for the batch
                embeddings = embedding_model.embed_documents(chunk_texts)

                for record, embedding in zip(batch, embeddings):
                    event_id = record[0]
                    chunk_id = record[1]
                    tic = record[2]
                    published_at = record[3]
                    url = record[4]
                    chunk = record[5]
                    chunk_hash = record[6]
                    raw_json_hash = record[7]

                    # Insert embedding into the database
                    cursor.execute("""
                        INSERT INTO core.news_embeddings (
                            event_id, chunk_id, tic, published_at, url, 
                            chunk_sha256, raw_json_sha256, 
                            embedding, embedding_model, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (tic, url, chunk_id) 
                        DO UPDATE SET
                            event_id = EXCLUDED.event_id,
                            chunk_id = EXCLUDED.chunk_id,
                            published_at = EXCLUDED.published_at,
                            chunk_sha256 = EXCLUDED.chunk_sha256,
                            raw_json_sha256 = EXCLUDED.raw_json_sha256,
                            embedding = EXCLUDED.embedding,
                            embedding_model = EXCLUDED.embedding_model,
                            updated_at = NOW()
                        WHERE core.news_embeddings.raw_json_sha256 <> EXCLUDED.raw_json_sha256
                            OR core.news_embeddings.chunk_sha256 <> EXCLUDED.chunk_sha256;
                    """, (
                        event_id, chunk_id, tic, published_at, url,
                        chunk_hash, raw_json_hash, embedding, embedding_model_name
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