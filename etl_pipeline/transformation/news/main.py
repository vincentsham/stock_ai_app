import time
import pandas as pd
from server.database.utils import connect_to_db, insert_records, read_sql_query
from states import News
from graph import create_graph
from tqdm import tqdm  # Import tqdm for progress tracking



def main():
    """Main function to execute the news analysis pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = """
                SELECT 
                    n.event_id,
                    n.tic,
                    n.url,
                    n.title,
                    n.content,
                    n.publisher,
                    n.published_at,
                    n.raw_json_sha256,
                    sp.name,
                    sp.industry,
                    sp.sector,
                    sp.short_summary
                FROM core.news AS n
                LEFT JOIN core.news_analysis AS a
                    ON n.tic = a.tic 
                    AND n.url = a.url
                LEFT JOIN core.stock_profiles AS sp
                    ON n.tic = sp.tic
                WHERE a.raw_json_sha256 IS NULL 
                OR n.raw_json_sha256 <> a.raw_json_sha256;
        """
        df = read_sql_query(query, conn)

    # Construct states from the retrieved records
    states = [
        (News(
            tic=row['tic'],
            company_name=row['name'],
            industry=row['industry'],
            sector=row['sector'],
            company_description=row['short_summary'],
            headline=row['title'],
            summary=row['content'],
            url=row['url'],
            publisher=row['publisher'],
            published_at=str(row['published_at'])  # Convert to string
        ), row['event_id'], row['raw_json_sha256'])  # Keep track of the event ID and hash
        for _, row in df.iterrows()
    ]

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()

    no_major_news = 0
    processed_data = []

    # Use tqdm to track progress
    for state in tqdm(states, desc="Processing states"):
        final_state = app.invoke(state[0])
        if "impact_magnitude" in final_state and final_state["impact_magnitude"] == 1:
            no_major_news += 1
        final_state["event_id"] = state[1]  # Add the event ID to the final state
        final_state["raw_json_sha256"] = state[2]  # Add the hash to the final state
        out = {
                    "event_id": final_state.get("event_id"),    
                    "tic": final_state.get("tic"),
                    "url": final_state.get("url"),
                    "title": final_state.get("headline"),
                    "content": final_state.get("summary"),
                    "publisher": final_state.get("publisher"),
                    "published_at": final_state.get("published_at"),
                    "category": final_state.get("category"),
                    "event_type": final_state.get("event_type"),
                    "time_horizon": final_state.get("time_horizon"),
                    "duration": final_state.get("duration"),
                    "impact_magnitude": final_state.get("impact_magnitude"),
                    "affected_dimensions": final_state.get("affected_dimensions"),
                    "sentiment": final_state.get("sentiment"),
                    "raw_json_sha256": final_state.get("raw_json_sha256")
                }
        processed_data.append(out)

    df = pd.DataFrame(processed_data)

    # Load processed data into core.news_analysis
    total_records = 0
    if conn:
        total_records = insert_records(conn, df, "core.news_analysis", ["tic", "url"])
        conn.close()

    # End timing
    end_time = time.time()
    print(f"Inserted/Updated {total_records} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of major news is {no_major_news}.")
    

if __name__ == "__main__":
    main()