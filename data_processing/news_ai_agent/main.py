import time
import pandas as pd
from server.database.utils import connect_to_db
from state import News
from graph import create_graph
from tqdm import tqdm  # Import tqdm for progress tracking

def insert_records(data, conn):
    """Insert processed data into core.news_analysis."""
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute("""
                    INSERT INTO core.news_analysis (
                        tic, url, title, content, publisher, published_date, category, event_type,
                        time_horizon, duration, impact_magnitude, affected_dimensions, sentiment
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tic, url) DO UPDATE
                    SET title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        publisher = EXCLUDED.publisher,
                        category = EXCLUDED.category,
                        event_type = EXCLUDED.event_type,
                        time_horizon = EXCLUDED.time_horizon,
                        duration = EXCLUDED.duration,
                        impact_magnitude = EXCLUDED.impact_magnitude,
                        affected_dimensions = EXCLUDED.affected_dimensions,
                        sentiment = EXCLUDED.sentiment;
                """, (
                    record.get("ticker"),
                    record.get("url"),
                    record.get("headline"),
                    record.get("summary"),
                    record.get("publisher"),
                    record.get("publish_date"),
                    record.get("category"),
                    record.get("event_type"),
                    record.get("time_horizon"),
                    record.get("duration"),
                    record.get("impact_magnitude"),
                    record.get("affected_dimensions"),
                    record.get("sentiment")
                ))
            conn.commit()
    except Exception as e:
        print(f"Error inserting analysis data: {e}")
        conn.rollback()

def main():
    """Main function to execute the news analysis pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = "SELECT * FROM raw.news;"
        df = pd.read_sql_query(query, conn)

    # Construct states from the retrieved records
    states = [
        News(
            ticker=row['tic'],
            headline=row['title'],
            summary=row['content'],
            url=row['url'],
            publisher=row['publisher'],
            publish_date=str(row['published_date'])  # Convert to string
        )
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
        final_state = app.invoke(state)
        if "impact_magnitude" in final_state and final_state["impact_magnitude"] == "major":
            no_major_news += 1
        processed_data.append(final_state)

    # Load processed data into core.news_analysis
    if conn:
        insert_records(processed_data, conn)
        conn.close()

    # End timing
    end_time = time.time()
    print(f"Processed {len(states)} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of major news is {no_major_news}.")
    

if __name__ == "__main__":
    main()