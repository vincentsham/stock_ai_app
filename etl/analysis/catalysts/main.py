import time
import uuid
import pandas as pd
from database.utils import connect_to_db, insert_records, read_sql_query
from states import catalyst_session_factory
from graph import create_graph
from tqdm import tqdm
from datetime import datetime, timezone
from langchain_openai import OpenAIEmbeddings
import os
from etl.utils import fix_quotes
import database.config


QUERY = """
    WITH global_watermark AS (
        SELECT MAX(date) as last_processed_date
        FROM core.catalyst_versions
        WHERE tic = '{tic}'
    ),
    all_deltas AS (
        SELECT 
            n.tic,
            EXTRACT(YEAR FROM n.published_at)::INT AS year,
            EXTRACT(MONTH FROM n.published_at)::INT AS month
        FROM core.news n
        CROSS JOIN global_watermark gw
        WHERE n.tic = '{tic}'
        AND n.published_at >= '2025-09-01'
        AND (gw.last_processed_date IS NULL OR n.published_at > gw.last_processed_date)

        UNION ALL

        SELECT 
            e.tic,
            EXTRACT(YEAR FROM e.earnings_date)::INT AS year,
            EXTRACT(MONTH FROM e.earnings_date)::INT AS month
        FROM core.earnings_transcripts e
        CROSS JOIN global_watermark gw
        WHERE e.tic = '{tic}'
        AND e.earnings_date >= '2025-09-01'
        AND (gw.last_processed_date IS NULL OR e.earnings_date > gw.last_processed_date)
    )
    SELECT 
        d.tic,
        sp.name, 
        sp.sector, 
        sp.industry, 
        sp.short_summary,
        d.year,
        d.month,
        COUNT(*) as total_new_records
    FROM all_deltas d
    JOIN core.stock_profiles sp ON d.tic = sp.tic
    GROUP BY 1, 2, 3, 4, 5, 6, 7
    ORDER BY d.year ASC, d.month ASC;
"""


def main(tic: str, top_k: int = 3, year: int = None, month: int = None,
         batch_size: int = 10, sleep_time: int = 65):
    conn = connect_to_db()
    if not conn:
        print("Could not connect to database.")
        return

    query = QUERY.format(tic=tic)
    df = read_sql_query(query, conn)
    # Construct states from the retrieved records
    states = []
    if year:
        df = df[(df['year'] == year)]
    if month:
        df = df[(df['month'] == month)]
    for _, row in df.iterrows():
        states.append(
            catalyst_session_factory(
                tic=row['tic'],
                company_name=row['name'],
                industry=row['industry'],
                sector=row['sector'],
                company_description=row['short_summary'],
                calendar_year=row['year'],
                calendar_month=row['month'],
                top_k=top_k,
            ))
        

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    start_time = time.time()
    total_invalid = 0
    total_create = 0
    total_update = 0

    for i, state in enumerate(tqdm(states, desc=f"Processing states - {tic}")):
        n_invalid = 0
        n_create = 0
        n_update = 0
        if i > 0 and i % batch_size == 0:
            print(f"\n[Rate Limit Protection] Processed {batch_size} items. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
        
        retries = 3
        while retries > 0:
            try:
                final_state = app.invoke(state)
                break
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    print(f"Hit rate limit on {tic}. Sleeping for {sleep_time}s before retry...")
                    time.sleep(sleep_time)
                retries -= 1
                if retries == 0:
                    print(f"Failed to process {tic} "
                          f"{state['query_params'].calendar_year}-{state['query_params'].calendar_month} "
                          f"after multiple retries: {e}")
                    break
                print(f"Error processing {tic}: {e}. Retrying...")
        if retries == 0:
            continue

        # Build chunk_map to derive dates from citation chunk_ids
        chunk_map = {chunk['chunk_id']: chunk for chunk in final_state.get("raw_chunks", [])}

        processed_data = []
        for catalyst in final_state.get("final_catalysts", []):
            n_create += 1 if catalyst.action == "create" else 0
            n_update += 1 if catalyst.action == "update" else 0
            n_invalid += 1 if not catalyst.is_valid else 0
    
            if catalyst.is_valid:
                # Derive date from the latest citation chunk
                citation_dates = [
                    chunk_map[c.chunk_id]['date']
                    for c in catalyst.citations if c.chunk_id in chunk_map
                ]
                catalyst_date = max(citation_dates) if citation_dates else None

                # Generate UUID for new catalysts
                catalyst_id = catalyst.catalyst_id if catalyst.catalyst_id else str(uuid.uuid4())

                out = {
                    "catalyst_id": catalyst_id,
                    "tic": final_state["company_info"].ticker,
                    "date": catalyst_date,
                    "catalyst_type": catalyst.catalyst_type,
                    "title": fix_quotes(catalyst.title),
                    "summary": fix_quotes(catalyst.summary),
                    "sentiment": catalyst.sentiment,
                    "time_horizon": catalyst.time_horizon,
                    "magnitude": catalyst.magnitude,
                    "impact_area": catalyst.impact_area,
                    "mention_count": len(catalyst.citations),
                    "chunk_ids": [c.chunk_id for c in catalyst.citations],
                    "citations": [fix_quotes(c.quote) for c in catalyst.citations],
                    "updated_at": datetime.now(timezone.utc),
                }
                processed_data.append(out)

        if not processed_data:
            continue

        try:
            df_out = pd.DataFrame(processed_data)
            # version_no is auto-assigned by DB trigger (trg_auto_version_no)
            # master table is auto-upserted by DB trigger (trg_upsert_catalyst_master)
            insert_records(conn, df_out, "core.catalyst_versions")
            print(f"\n{tic} — Create: {n_create}, Update: {n_update}, Invalid: {n_invalid}, Total: {n_create + n_update + n_invalid}")
            total_invalid += n_invalid
            total_create += n_create
            total_update += n_update

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error processing catalysts for {tic}: {e}")
            raise e

    conn.close()
    end_time = time.time()
    print(f"\n{tic} — Total Create: {total_create}, Total Update: {total_update}, Invalid: {total_invalid}, Total: {total_create + total_update + total_invalid}")
    print(f"Catalyst AI Agent completed in {end_time - start_time:.2f} seconds.")

    return


if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        conn.close()
        batch_size = 10  # number of companies to process before sleeping
        sleep_time = 65  # seconds to sleep between batches to avoid rate limits
        for i, record in enumerate(records):
            print(f"\nProcessing {record[0]} ({i+1}/{len(records)})...")
            # if i <= 1:
            #     continue  # Skip the first 2 records for testing
            if i > 0 and i % 2 == 0:
                print(f"\n[Rate Limit Protection] Processed {2} items. Sleeping for {125} seconds...")
                time.sleep(125)
            tic = record[0]
            main(tic=tic, top_k=3, batch_size=batch_size, sleep_time=sleep_time)
        # main(tic="AAPL", top_k=3)
        # main(tic="NVDA", top_k=3)
        # main(tic="TSLA", top_k=3)


