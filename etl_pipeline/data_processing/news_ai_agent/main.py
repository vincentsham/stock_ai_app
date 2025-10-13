import time
import pandas as pd
from server.database.utils import connect_to_db
from states import News
from graph import create_graph
from tqdm import tqdm  # Import tqdm for progress tracking
from etl_pipeline.utils import read_sql_query

def insert_records(data, conn):
    """Insert processed data into core.news_analysis."""
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute("""
                    INSERT INTO core.news_analysis (
                        tic, url, title, content, publisher, published_date, category, event_type,
                        time_horizon, duration, impact_magnitude, affected_dimensions, sentiment,
                        raw_json_sha256, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                        sentiment = EXCLUDED.sentiment,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW()
                    WHERE core.news_analysis.raw_json_sha256 <> EXCLUDED.raw_json_sha256;
                """, (
                    record.get("tic"),
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
                    record.get("sentiment"),
                    record.get("raw_json_sha256")
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
        query = """
                SELECT 
                    n.tic,
                    n.url,
                    n.title,
                    n.content,
                    n.publisher,
                    n.published_date,
                    n.raw_json_sha256,
                    sp.name,
                    sp.industry,
                    sp.sector,
                    sp.short_summary
                FROM raw.news AS n
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
            publish_date=str(row['published_date'])  # Convert to string
        ), row['raw_json_sha256'])  # Keep track of the hash
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
        final_state["raw_json_sha256"] = state[1]  # Add the hash to the final state
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