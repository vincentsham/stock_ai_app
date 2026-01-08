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
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import os
from etl.utils import fix_quotes


# Load environment variables
load_dotenv()

# Initialize the embedding model
embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL")
embedding_model = OpenAIEmbeddings(model=embedding_model_name)



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
            WHERE n.tic = '{tic}'
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
            WHERE e.tic = '{tic}'
            ORDER BY e.tic, e.calendar_year, e.calendar_quarter;
        """
    }
}


QUERY_UPDATE = {
    "news": {
        "monthly": 
        """
        WITH global_watermark AS (
                -- 1. Find the SINGLE latest catalyst date for this stock
                SELECT MAX(date) as last_run_date
                FROM core.catalyst_versions
                WHERE tic = '{tic}'
                AND source_type = 'news'
            ),
            news_grouped AS (
                -- 2. Group news by month (same as before)
                SELECT
                    n.tic,
                    DATE_TRUNC('month', n.published_at)::DATE AS news_month,
                    COUNT(*) AS record_count,
                    MAX(n.published_at) AS latest_news_ts
                FROM core.news n
                WHERE n.tic = '{tic}'
                AND n.published_at >= '2026-01-01'
                GROUP BY 1, 2
            )
            SELECT 
                ng.tic,
                EXTRACT(YEAR FROM ng.news_month)::INT AS year,
                NULL AS quarter,
                EXTRACT(MONTH FROM ng.news_month)::INT AS month,
                ng.record_count,
                sp.name, 
                sp.sector, 
                sp.industry, 
                sp.short_summary
            FROM news_grouped ng
            JOIN core.stock_profiles sp ON ng.tic = sp.tic
            CROSS JOIN global_watermark gw
            WHERE 
                -- 3. ONLY select if news is newer than the global high water mark
                -- (If no catalyst exists yet (NULL), we take everything)
                gw.last_run_date IS NULL
                OR ng.latest_news_ts > gw.last_run_date
            ORDER BY ng.news_month ASC;
        """
    },
    "earnings_transcript": {
        "quarterly": 
        """
        SELECT 
                e.tic, 
                e.calendar_year AS year, 
                e.calendar_quarter AS quarter, 
                NULL AS month,
                sp.name, 
                sp.sector, 
                sp.industry, 
                sp.short_summary
            FROM core.earnings_transcripts e
            JOIN core.stock_profiles sp 
                ON e.tic = sp.tic
            LEFT JOIN core.catalyst_versions c
                ON c.event_id = e.event_id
                AND c.source_type = 'earnings_transcript'
            WHERE e.tic = '{tic}'
            AND e.calendar_year >= 2025
            AND (
                c.event_id IS NULL
                OR e.raw_json_sha256 IS DISTINCT FROM c.raw_json_sha256
            )
            ORDER BY e.calendar_year ASC, e.calendar_quarter ASC;
        """
    }
}



QUERY_NO_TIC = {
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
                                         'state', 'sentiment', 'time_horizon','impact_magnitude', 
                                         'certainty', 'impact_area', 'mention_count', 'event_ids',
                                         'created_at', 'updated_at'],
    "catalyst_versions": ['event_id', 'chunk_id', 'catalyst_id', 'tic', 'date', 'catalyst_type', 'title', 'summary',
                                         'evidence', 'state', 'sentiment', 'time_horizon','impact_magnitude', 
                                         'certainty', 'impact_area', 'is_valid', 'rejection_reason', 
                                         'ingestion_batch', 'source_type', 'source', 
                                         'url', 'raw_json_sha256', 'updated_at'],
    "catalyst_master_embeddings": ['catalyst_id', 'embedding', 'embedding_model', 'updated_at'],
    "catalyst_version_embeddings": ['event_id', 'chunk_id', 'catalyst_id', 'catalyst_type', 'embedding', 'embedding_model', 'updated_at'],
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
        # print("No records to update in catalyst_master.")
        return 0
    # Step 1: Query existing records from core.catalyst_versions
    query = f"""
        SELECT cv.*, cve.embedding AS embedding, cve.embedding_model AS embedding_model, cm.created_at
        FROM core.catalyst_versions AS cv
        JOIN core.catalyst_master AS cm
        ON cv.catalyst_id = cm.catalyst_id
        JOIN core.catalyst_version_embeddings AS cve
        ON cv.catalyst_id = cve.catalyst_id
            AND cv.event_id = cve.event_id
            AND cv.chunk_id = cve.chunk_id 
        WHERE cv.catalyst_id IN ({', '.join([f"'{cid}'" for cid in df['catalyst_id'].dropna().unique()])});
    """
    existing_df = read_sql_query(query, conn)

    if existing_df.empty:
        raise ValueError("No existing records found for the provided catalyst_ids.")

    # Step 2: Extract the latest record for each catalyst_id based on both date DESC and updated_at DESC
    existing_df = existing_df.sort_values(by=['catalyst_id', 'date', 'updated_at'], ascending=[True, False, False])
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
    total_records = insert_records(conn, latest_records[columns['catalyst_master_embeddings']], 
                                   'core.catalyst_master_embeddings', keys=['catalyst_id'], updated_at=False)
    

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




def main(tic: str, type: Literal["news", "earnings_transcript"] = "news",
         frequency: Literal["daily", "monthly", "quarterly"] = "monthly",
         top_k: int = 3, year: int = None, quarter: int = None, month: int = None,
         batch_size: int = 10, sleep_time: int = 65, idx: int = 0):
    # Connect to the database
    conn = connect_to_db()
    if conn:
        if year is not None:
            if tic is None:
                query = QUERY_NO_TIC[type][frequency]
            else:
                query = QUERY[type][frequency].format(tic=tic)
            df = read_sql_query(query, conn)
            if year is not None:
                df = df[df['year'] == year]
            if quarter is not None:
                df = df[df['quarter'] == quarter]
            if month is not None:
                df = df[df['month'] == month]
        else:
            query = QUERY_UPDATE[type][frequency].format(tic=tic)
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
                    top_k=top_k,
                ))

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    total_new_records = 0
    total_existing_records = 0
    total_updated_master_records = 0
    retries = 3

    n_skip = 0
    n_keep = 0
    n_create = 0
    n_update = 0
    n_valid = 0
    n = 0

    # Use tqdm to track progress
    for i, state in enumerate(tqdm(states, desc=f"Processing states - {type}{' - ' + tic if tic else ''} - {frequency}")):
        if i < idx - 1:
            continue
        # Batch Sleep Logic
        if i > 0 and i % batch_size == 0:
            print(f"\n[Rate Limit Protection] Processed {batch_size} items. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
        
        while retries > 0:
            try:
                final_state = app.invoke(state)
                retries = 3  # reset retries for next state
                break
            except Exception as e:
                # Optional: If error is specifically RateLimitError, force a sleep immediately
                if "rate limit" in str(e).lower() or "429" in str(e):
                    print(f"Hit rate limit immediately on {state.company_info.tic}. Sleeping for {sleep_time}s before retry...")
                    time.sleep(sleep_time)
                
                retries -= 1
                if retries == 0:
                    print(f"Failed to process {state.company_info.tic} "
                          f"{state.query_params.source_type}: {state.query_params.catalyst_type} for "
                          f"{state.query_params.calendar_year}-{state.query_params.calendar_quarter if state.query_params.calendar_quarter else ''}{state.query_params.calendar_month if state.query_params.calendar_month else ''} "
                          f"after multiple retries: {e}")
                    # Decide if you want to raise e or continue. Continuing prevents one failure from stopping the batch.
                    # raise e 
                    break 
                print(f"Error processing {state.company_info.tic}: {e}. Retrying...")
        if retries == 0:
            retries = 3  # reset for next state
            continue  # skip to next state after exhausting retries
        processed_data = []
        for catalyst in final_state.get("catalysts", []):
            n_skip += 1 if catalyst.action == "skip" else 0
            n_keep += 1 if catalyst.action == "keep" else 0
            n_create += 1 if catalyst.action == "create" else 0
            n_update += 1 if catalyst.action == "update" else 0
            n_valid += 1 if catalyst.candidate.is_valid == 1 else 0
            n += 1
            if catalyst.candidate.is_catalyst == 1:
                out = {
                        "event_id": catalyst.chunk.event_id,
                        "chunk_id": catalyst.chunk.chunk_id,
                        "catalyst_id": catalyst.candidate.catalyst_id,
                        "tic": final_state.get("company_info", {}).tic,
                        "date": catalyst.chunk.date,
                        "catalyst_type": catalyst.candidate.catalyst_type,
                        "title": fix_quotes(catalyst.candidate.title),
                        "summary": fix_quotes(catalyst.candidate.summary),
                        "evidence": fix_quotes(catalyst.candidate.evidence),
                        "state": catalyst.candidate.state,
                        "sentiment": catalyst.candidate.sentiment,
                        "time_horizon": catalyst.candidate.time_horizon,
                        "impact_magnitude": catalyst.candidate.impact_magnitude,
                        "certainty": catalyst.candidate.certainty,
                        "impact_area": catalyst.candidate.impact_area,
                        "is_valid": catalyst.candidate.is_valid,
                        "rejection_reason": fix_quotes(catalyst.candidate.rejection_reason),
                        "ingestion_batch": frequency,
                        "source_type": final_state.get("query_params", {}).source_type,
                        "source": catalyst.chunk.source,
                        "url": catalyst.chunk.url,
                        "raw_json_sha256": catalyst.chunk.raw_json_sha256,
                }
                processed_data.append(out)

        # Clean "null" strings in UUID columns before inserting records
        # df = clean_null_strings(df, ['catalyst_id', 'event_id'])

        # print(f"Total number of records is {len(processed_data)}.")
        try:
            if conn:
                df = pd.DataFrame(processed_data)
                if df.empty:
                    continue
                _total_new_records = 0
                _total_existing_records = 0
                _total_updated_master_records = 0

                df['embedding'] = None
                df['embedding_model'] = None

                mask = df['title'].notnull()
                embeddings = embedding_model.embed_documents(df.loc[mask,'title'].tolist())
                df.loc[mask,'embedding'] = pd.Series(list(embeddings), index=df.index[mask])
                df.loc[mask,'embedding_model'] = embedding_model_name
                if len(df[df["state"] == "announced"]) > 0:

                    new_records = df[df["state"] == "announced"].copy()
                    new_records['created_at'] = datetime.now(timezone.utc)
                    new_records['updated_at'] = new_records['created_at']
                    new_records['mention_count'] = new_records['is_valid']
                    new_records['event_ids'] = new_records.apply(
                                                    lambda row: [row['event_id']] if row['is_valid'] == 1 else [],
                                                    axis=1,
                                                )
                    insert_records(conn, 
                                new_records[columns['catalyst_master']], 
                                "core.catalyst_master")
                    insert_records(conn, 
                                new_records[columns['catalyst_master_embeddings']], 
                                "core.catalyst_master_embeddings")                    
                    _total_new_records = insert_records(conn, 
                                new_records[columns['catalyst_versions']],
                                "core.catalyst_versions")
                    insert_records(conn, 
                                new_records[columns['catalyst_version_embeddings']],
                                "core.catalyst_version_embeddings")

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
                    insert_records(conn,
                                existing_records[columns['catalyst_version_embeddings']],
                                "core.catalyst_version_embeddings", 
                                keys=['event_id', 'chunk_id', 'catalyst_id'],
                                updated_at=False)
                    
                    total_existing_records += _total_existing_records
                    _total_updated_master_records = update_master(conn, existing_records[existing_records['is_valid'] == 1])
                    total_updated_master_records += _total_updated_master_records
                print(f"{final_state.get('company_info', {}).tic} - {final_state.get('query_params', {}).catalyst_type}: Total records processed: {len(processed_data)}, "
                      f"New records inserted: {_total_new_records}, Existing records updated: {_total_existing_records}, "
                      f"Master records updated: {_total_updated_master_records}")
                print(f"Actions so far - Skip: {n_skip}, Keep: {n_keep}, Create: {n_create}, Update: {n_update}, Valid: {n_valid}, Total Processed Catalysts: {n}")

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
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            # main(tic = tic, type="news", top_k=1, frequency="monthly", year=2025, batch_size=5, sleep_time=185)
            main(tic=tic, type="earnings_transcript", frequency="quarterly", top_k=1, year=None, batch_size=5, sleep_time=125)
            # time.sleep(125)
            main(tic=tic, type="news", frequency="monthly", top_k=1, year=None, batch_size=5, sleep_time=125)
            # time.sleep(125)
        conn.close()


