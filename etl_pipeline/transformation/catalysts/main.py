import time
from typing_extensions import Literal
import pandas as pd
from database.utils import connect_to_db, insert_records, read_sql_query
from states import catalyst_session_factory
from graph import create_graph
from tqdm import tqdm
from prompts import CATALYST_QUERIES
from datetime import datetime, timedelta, timezone
import uuid


QUERY = {
    "news": {
        "monthly": 
        """
            WITH news_summary AS (
            SELECT
                n.tic,
                EXTRACT(YEAR FROM n.published_at)::INT AS year,
                EXTRACT(MONTH FROM n.published_at)::INT AS month,
                COUNT(*) AS record_count
            FROM core.news n
            GROUP BY n.tic, year, month
            )
            SELECT n.tic, n.year, NULL AS quarter, n.month, n.record_count,
                sp.name, sp.sector, sp.industry, sp.short_summary
            FROM news_summary n
            JOIN core.stock_profiles AS sp
                ON n.tic = sp.tic
            ORDER BY n.tic, n.year, n.month;
        """
    }
,
    "earnings_transcript": {
        "quarterly": 
        """
            SELECT e.tic, e.calendar_year AS year, e.calendar_quarter AS quarter, NULL AS month,
                sp.name, sp.sector, sp.industry, sp.short_summary
            FROM core.earnings_transcripts e
            JOIN core.stock_profiles AS sp
                ON e.tic = sp.tic
            ORDER BY e.tic, e.calendar_year, e.calendar_quarter;
        """
    }
}

columns = {
    "catalyst_master": ['catalyst_id', 'tic', 'date', 'catalyst_type', 'title', 'summary',
                                         'evidence', 'state', 'sentiment', 'time_horizon','impact_magnitude', 
                                         'certainty', 'impact_area', 'mention_count', 'event_ids',
                                         'created_at', 'updated_at'],
    "catalyst_versions": ['event_id', 'chunk_id', 'catalyst_id', 'tic', 'date', 'catalyst_type', 'title', 'summary',
                                         'evidence', 'state', 'sentiment', 'time_horizon','impact_magnitude', 
                                         'certainty', 'impact_area', 'ingestion_batch', 'source_type', 'source', 
                                         'url', 'raw_json_sha256', 'updated_at']
}


def update_master(conn, df: pd.DataFrame):
    """
    Update the core.catalyst_master table with new catalysts from the provided DataFrame.
    1. Query records from core.catalyst_versions where the catalyst_id is in the DataFrame.
    2. Extract the latest record for each catalyst_id.
    3. Aggregate mention_count and urls for each catalyst_id.
    4. Update core.catalyst_master with the aggregated data.
    """
    if df.empty:
        print("No records to update in catalyst_master.")
        return 0
    # Step 1: Query existing records from core.catalyst_versions
    query = f"""
        SELECT cv.*, cm.created_at
        FROM core.catalyst_versions AS cv
        JOIN core.catalyst_master AS cm
        ON cv.catalyst_id = cm.catalyst_id
        WHERE cv.catalyst_id IN ({', '.join([f"'{cid}'" for cid in df['catalyst_id'].dropna().unique()])});
    """
    existing_df = read_sql_query(query, conn)

    if existing_df.empty:
        raise ValueError("No existing records found for the provided catalyst_ids.")

    # Step 2: Extract the latest record for each catalyst_id based on both date DESC and updated_at DESC
    existing_df = existing_df.sort_values(by=['catalyst_id', 'updated_at'], ascending=[True, False])
    latest_records = existing_df.groupby('catalyst_id').first().reset_index()

    # Step 3: Count how many records for mention_count and make a list of urls grouped by catalyst_id
    aggregated_data = existing_df.groupby('catalyst_id').agg(
        # event_id unique count
        mention_count=('event_id', 'nunique'),
        event_ids=('event_id', lambda x: list(x.dropna().unique()))
    ).reset_index()

    # Step 3.5: Add latest records with mention_count and urls from aggregated data
    latest_records = latest_records.merge(aggregated_data, on='catalyst_id')

    # Step 4: Update core.catalyst_master
    total_records = insert_records(conn, latest_records[columns['catalyst_master']], 
                                   'core.catalyst_master', keys=['catalyst_id'], updated_at=False)
    return total_records


def get_catalyst_id_list(conn, tic: str, catalyst_type: str) -> list:
    query = f"""
        SELECT catalyst_id
        FROM core.catalyst_master
        WHERE tic = '{tic}' AND catalyst_type = '{catalyst_type}';
    """
    df = read_sql_query(query, conn)
    # Extract the catalyst_id values and change to str and put into a list
    catalyst_id_list = df['catalyst_id'].astype(str).tolist()
    return catalyst_id_list


def main(type: Literal["news", "earnings_transcript"] = "news",
         frequency: Literal["daily", "monthly", "quarterly"] = "monthly"):
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = QUERY[type][frequency]
        df = read_sql_query(query, conn)
    else:
        print("Could not connect to database.")
        return

    # Construct states from the retrieved records
    states = []
    for _, row in df.iterrows():
        for catalyst_type in CATALYST_QUERIES.keys():
            states.append(
                catalyst_session_factory(
                    tic=row['tic'],
                    company_name=row['name'],
                    industry=row['industry'],
                    sector=row['sector'],
                    company_description=row['short_summary'],
                    calendar_year=row['year'],
                    calendar_quarter=row['quarter'],
                    calendar_month=row['month'],
                    source_type=type,
                    catalyst_type=catalyst_type,
                    top_k=3
                ))

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    total_new_records = 0
    total_existing_records = 0
    total_updated_master_records = 0

    # Use tqdm to track progress
    for state in tqdm(states, desc="Processing company profiles"):
        final_state = app.invoke(state)
        processed_data = []
        for catalyst in final_state.get("catalysts", []):
            if catalyst.candidate.is_catalyst == 1:
                out = {
                        "event_id": catalyst.chunk.event_id,
                        "chunk_id": catalyst.chunk.chunk_id,
                        "catalyst_id": catalyst.candidate.catalyst_id,
                        "tic": final_state.get("company_info", {}).tic,
                        "date": catalyst.chunk.date,
                        "catalyst_type": catalyst.candidate.catalyst_type,
                        "title": catalyst.candidate.title,
                        "summary": catalyst.candidate.summary,
                        "evidence": catalyst.candidate.evidence,
                        "state": catalyst.candidate.state,
                        "sentiment": catalyst.candidate.sentiment,
                        "time_horizon": catalyst.candidate.time_horizon,
                        "impact_magnitude": catalyst.candidate.impact_magnitude,
                        "certainty": catalyst.candidate.certainty,
                        "impact_area": catalyst.candidate.impact_area,
                        "ingestion_batch": frequency,
                        "source_type": final_state.get("query_params", {}).source_type,
                        "source": catalyst.chunk.source,
                        "url": catalyst.chunk.url,
                        "raw_json_sha256": catalyst.chunk.raw_json_sha256,
                }
                processed_data.append(out)

        # print(f"Total number of records is {len(processed_data)}.")
        try:
            if conn:
                df = pd.DataFrame(processed_data)
                if df.empty:
                    continue
                _total_new_records = 0
                _total_existing_records = 0
                _total_updated_master_records = 0
                if len(df[df["state"] == "announced"]) > 0:
                    new_records = df[df["state"] == "announced"].copy()
                    new_records['mention_count'] = 1
                    new_records['event_ids'] = new_records['event_id'].apply(lambda x: [x] if pd.notna(x) else [])
                    new_records['created_at'] = datetime.now(timezone.utc)
                    new_records['updated_at'] = new_records['created_at']

                    insert_records(conn, 
                                new_records[columns['catalyst_master']], 
                                "core.catalyst_master")
                    _total_new_records = insert_records(conn, 
                                new_records[columns['catalyst_versions']],
                                "core.catalyst_versions")
                    total_new_records += _total_new_records

                catalyst_id_list = get_catalyst_id_list(conn, 
                                                        final_state.get('company_info', {}).tic, 
                                                        final_state.get('query_params', {}).catalyst_type)
                if len(df[(df["catalyst_id"].isin(catalyst_id_list)) & (df["state"] != "announced")]) > 0:
                    existing_records = df[(df["catalyst_id"].isin(catalyst_id_list)) & (df["state"] != "announced")].copy()
                    base_time = datetime.now(timezone.utc)
                    existing_records["updated_at"] = [base_time + timedelta(milliseconds=i) for i in range(len(existing_records))]
                    _total_existing_records = insert_records(conn, 
                                existing_records[columns['catalyst_versions']],
                                "core.catalyst_versions", 
                                keys=['event_id', 'chunk_id', 'catalyst_id'],
                                updated_at=False)
                    total_existing_records += _total_existing_records
                    _total_updated_master_records = update_master(conn, existing_records)
                    total_updated_master_records += _total_updated_master_records
                print(f"{final_state.get('company_info', {}).tic}: Total records processed: {len(processed_data)}, "
                      f"New records inserted: {_total_new_records}, Existing records updated: {_total_existing_records}, "
                      f"Master records updated: {_total_updated_master_records}")

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error processing catalysts for {final_state.get('company_info', {}).tic}: {e}")
            raise e

    conn.close()
    end_time = time.time()
    print(f"Total new records inserted: {total_new_records}")
    print(f"Total existing records updated: {total_existing_records}")
    print(f"Total master records updated: {total_updated_master_records}")
    print(f"ETL process completed in {end_time - start_time:.2f} seconds.")
    
    return

if __name__ == "__main__":
    main("earnings_transcript", "quarterly")
    main("news", "monthly")