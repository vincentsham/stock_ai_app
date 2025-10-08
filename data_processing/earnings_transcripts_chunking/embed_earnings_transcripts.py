import os
from server.database.utils import connect_to_db
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm



# Load environment variables
load_dotenv()

# Initialize the embedding model
embedding_model_name = "text-embedding-3-small"
embedding_model = OpenAIEmbeddings(model=embedding_model_name)

# Main function to process and store embeddings
def process_and_store_embeddings():
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            # Fetch chunks without embeddings
            cursor.execute("""
                SELECT tic, fiscal_year, fiscal_quarter, earnings_date, chunk_id, chunk
                FROM core.earnings_transcript_chunks
                WHERE NOT EXISTS (
                    SELECT 1 FROM core.earnings_transcript_embeddings e
                    WHERE e.tic = core.earnings_transcript_chunks.tic
                        AND e.fiscal_year = core.earnings_transcript_chunks.fiscal_year
                        AND e.fiscal_quarter = core.earnings_transcript_chunks.fiscal_quarter
                        AND e.chunk_id = core.earnings_transcript_chunks.chunk_id
                );
            """)
            records = cursor.fetchall()

            # Define batch size
            batch_size = 32

            # Add tqdm progress bar
            for i in tqdm(range(0, len(records), batch_size), desc="Processing batches"):
                batch = records[i:i + batch_size]

                # Prepare batch chunks for embedding
                chunk_texts = [record[5] for record in batch]

                # Generate embeddings for the batch
                embeddings = embedding_model.embed_documents(chunk_texts)

                for record, embedding in zip(batch, embeddings):
                    tic = record[0]
                    fiscal_year = record[1]
                    fiscal_quarter = record[2]
                    earnings_date = record[3]
                    chunk_id = record[4]

                    # Insert embedding into the database
                    cursor.execute("""
                        INSERT INTO core.earnings_transcript_embeddings (
                            tic, fiscal_year, fiscal_quarter, earnings_date, chunk_id, embedding, embedding_model
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tic, fiscal_year, fiscal_quarter, chunk_id) DO NOTHING;
                    """, (
                        tic, fiscal_year, fiscal_quarter, earnings_date, chunk_id, embedding, embedding_model_name
                    ))

            conn.commit()
            print("Embeddings processed and stored successfully.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

if __name__ == "__main__":
    process_and_store_embeddings()
    # connect_to_db()