import time
import pandas as pd
from database.utils import connect_to_db, read_sql_query, insert_records
from states import Signal
from graph import create_graph
from tqdm import tqdm
from typing import Literal


QUERY = {
    "news": 
        """
            SELECT n.tic, n.published_at, n.url, n.event_id, n.chunk_id, 
                n.chunk_sha256, n.raw_json_sha256, n.chunk,
                sp.name, sp.sector, sp.industry, sp.short_summary
            FROM core.news_chunks AS n
            JOIN core.stock_profiles AS sp
                ON n.tic = sp.tic
            ORDER BY n.published_at DESC;
        """,
    "earnings_transcript": 
        """
            SELECT e.tic, e.calendar_year, e.calendar_quarter,
                e.event_id, e.chunk_id,
                e.chunk_sha256, e.transcript_sha256, e.chunk,
                sp.name, sp.sector, sp.industry, sp.short_summary
            FROM core.earnings_transcript_chunks AS e
            JOIN core.stock_profiles AS sp
                ON e.tic = sp.tic
            ORDER BY e.calendar_year DESC, e.calendar_quarter DESC;
        """
}

COLUMNS = {
    "news": [
        "tic", "event_id", "chunk_id", "chunk_sha256", "raw_json_sha256",
        "is_signal", "reason"
    ],
    "earnings_transcript": [
        "tic", "event_id", "chunk_id", "chunk_sha256", "transcript_sha256",
        "is_signal", "reason"
    ]
}


def main(type: Literal["news", "earnings_transcript"] = "news"):
    """Main function to execute the content signal classification pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = QUERY[type]
        df = read_sql_query(query, conn)
        
    else:
        print("Could not connect to database.")
        return

    # Construct states from the retrieved records
    states = []
    for _, row in df.iterrows():
        company_info = {
            "tic": row['tic'],
            "company_name": row['name'],
            "sector": row['sector'],
            "industry": row['industry'],
            "short_description": row['short_summary']
        }
        state = Signal(
            company_info=company_info,
            content=row['chunk'],
            is_signal=0,
            reason=""
        )
        df = {
            "tic": row['tic'],
            "event_id": row['event_id'],
            "chunk_id": row['chunk_id'],
            "chunk_sha256": row['chunk_sha256'],
            "raw_json_sha256": row['raw_json_sha256'] if type == "news" else None,
            "transcript_sha256": row['transcript_sha256'] if type == "earnings_transcript" else None,
        }
        states.append((state, df))

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    processed_data = []
    retries = 3

    # Use tqdm to track progress
    for state in tqdm(states, desc="Processing company profiles"):
        while retries > 0:
            try:
                final_state = app.invoke(state[0])
                retries = 3  # reset retries for next state
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    print(f"Failed to process {state[1]['event_id']} after multiple retries: {e}")
                    raise e
                print(f"Error processing {state[1]['event_id']}: {e}. Retrying...")
        df = state[1]
        df['is_signal'] = final_state['is_signal']
        df['reason'] = final_state['reason']
        processed_data.append(df)
    # Load processed data into core.stock_metadata
    total_records = 0
    if conn:
        processed_data = pd.DataFrame(processed_data)
        processed_data = processed_data[COLUMNS[type]]
        total_records = insert_records(conn, processed_data, f'core.{type}_chunk_signal', ['event_id', 'chunk_id'])
        

        conn.close()

    # End timing
    end_time = time.time()
    print(f"Processed {len(states)} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of records is {total_records}.")

if __name__ == "__main__":
    main("news")
    # main("earnings_transcript")