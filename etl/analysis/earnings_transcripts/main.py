import time
import os
import pandas as pd
from database.utils import connect_to_db, insert_records, read_sql_query
from states import merged_state_factory, MergedState
from graph import create_graph
from tqdm import tqdm
import ast
from etl.utils import fix_quotes



def main(tic: str, calendar_year: int = 2024, calendar_quarter: int = 4, sleep_time: int = None):
    """Main function to execute the stock profile summarization pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        if calendar_year is None or calendar_quarter is None:
            query_latest_year_quarter = """
            SELECT calendar_year, calendar_quarter
            FROM core.earnings_transcript_analysis
            WHERE tic = %s
            ORDER BY calendar_year DESC, calendar_quarter DESC
            LIMIT 1;
            """
            latest_df = read_sql_query(query_latest_year_quarter, conn, params=(tic,))
            if not latest_df.empty:
                calendar_year = int(latest_df.loc[0, 'calendar_year'])
                calendar_quarter = int(latest_df.loc[0, 'calendar_quarter'])
                query = """
                    SELECT et.event_id, et.tic, sm.name, sm.sector, sm.industry, sm.short_summary, 
                        et.calendar_year, et.calendar_quarter, et.earnings_date, et.transcript_sha256
                    FROM core.earnings_transcripts AS et
                    LEFT JOIN core.earnings_transcript_analysis AS eta
                    ON et.tic = eta.tic
                        AND et.calendar_year = eta.calendar_year
                        AND et.calendar_quarter = eta.calendar_quarter
                    JOIN core.stock_profiles AS sm 
                    ON et.tic = sm.tic
                    WHERE et.tic = %s
                        AND (et.calendar_year, et.calendar_quarter) > (%s, %s)
                        AND et.calendar_year >= 2025
                        AND et.transcript_sha256 IS DISTINCT FROM eta.transcript_sha256;
                """
                query_params = (tic, calendar_year, calendar_quarter)
            else:
                query = """
                    SELECT et.event_id, et.tic, sm.name, sm.sector, sm.industry, sm.short_summary, 
                        et.calendar_year, et.calendar_quarter, et.earnings_date, et.transcript_sha256
                    FROM core.earnings_transcripts AS et
                    LEFT JOIN core.earnings_transcript_analysis AS eta
                    ON et.tic = eta.tic
                        AND et.calendar_year = eta.calendar_year
                        AND et.calendar_quarter = eta.calendar_quarter
                    JOIN core.stock_profiles AS sm 
                    ON et.tic = sm.tic
                    WHERE et.tic = %s
                        AND et.calendar_year >= 2025
                        AND et.transcript_sha256 IS DISTINCT FROM eta.transcript_sha256;
                """
                query_params = (tic,)
        else:
            query = """
                SELECT et.event_id, et.tic, sm.name, sm.sector, sm.industry, sm.short_summary, 
                    et.calendar_year, et.calendar_quarter, et.earnings_date, et.transcript_sha256
                FROM core.earnings_transcripts AS et
                LEFT JOIN core.earnings_transcript_analysis AS eta
                ON et.tic = eta.tic
                    AND et.calendar_year = eta.calendar_year
                    AND et.calendar_quarter = eta.calendar_quarter
                JOIN core.stock_profiles AS sm 
                ON et.tic = sm.tic
                WHERE et.tic = %s
                    AND (et.calendar_year, et.calendar_quarter) = (%s, %s)
                    AND et.transcript_sha256 IS DISTINCT FROM eta.transcript_sha256;
            """
            query_params = (tic, calendar_year, calendar_quarter)
        df = read_sql_query(query, conn, params=query_params)

        if df.empty:
            print(f"No new or updated earnings transcripts to process. - {tic}")
            return
    else:
        print("Could not connect to database.")
        return



    # Construct states from the retrieved records
    states = [
        (merged_state_factory(
            tic=row['tic'],
            company_name=row['name'],
            sector=row['sector'],
            industry=row['industry'],
            company_description=row['short_summary'],
            calendar_year=row['calendar_year'],
            calendar_quarter=row['calendar_quarter'],
            earnings_date=row['earnings_date'].isoformat()
        ), row['event_id'], row['transcript_sha256'])
        for _, row in df.iterrows()
    ]


    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    processed_data = []

    # Use tqdm to track progress
    for state in tqdm(states, desc=f"Processing earnings transcripts - {tic} - {calendar_year} Q{calendar_quarter}"):
        retries = 5
        while retries > 0:
            try:
                final_state = app.invoke(state[0])
                final_state['event_id'] = state[1]  # Add event_id to the final state
                final_state['transcript_sha256'] = state[2]  # Add transcript_sha256 to the final state
                out = {
                    "event_id": final_state.get("event_id"),
                    "tic": final_state.get("company_info", {}).get("tic"),
                    "calendar_year": final_state.get("company_info", {}).get("calendar_year"),
                    "calendar_quarter": final_state.get("company_info", {}).get("calendar_quarter"),
                    "sentiment": final_state.get("past_analysis", {}).get("sentiment"),
                    "durability": final_state.get("past_analysis", {}).get("durability"),
                    "performance_factors": final_state.get("past_analysis", {}).get("performance_factors"),
                    "past_summary": fix_quotes(final_state.get("past_analysis", {}).get("past_summary")),
                    "guidance_direction": final_state.get("future_analysis", {}).get("guidance_direction"),
                    "revenue_outlook": final_state.get("future_analysis", {}).get("revenue_outlook"),
                    "margin_outlook": final_state.get("future_analysis", {}).get("margin_outlook"),
                    "earnings_outlook": final_state.get("future_analysis", {}).get("earnings_outlook"),
                    "cashflow_outlook": final_state.get("future_analysis", {}).get("cashflow_outlook"),
                    "growth_acceleration": final_state.get("future_analysis", {}).get("growth_acceleration"),
                    "future_outlook_sentiment": final_state.get("future_analysis", {}).get("future_outlook_sentiment"),
                    "growth_drivers": final_state.get("future_analysis", {}).get("growth_drivers"),
                    "future_summary": fix_quotes(final_state.get("future_analysis", {}).get("future_summary")),
                    "risk_mentioned": final_state.get("risk_analysis", {}).get("risk_mentioned"),
                    "risk_impact": final_state.get("risk_analysis", {}).get("risk_impact"),
                    "risk_time_horizon": final_state.get("risk_analysis", {}).get("risk_time_horizon"),
                    "risk_factors": final_state.get("risk_analysis", {}).get("risk_factors"),
                    "risk_summary": fix_quotes(final_state.get("risk_analysis", {}).get("risk_summary")),
                    "mitigation_mentioned": final_state.get("risk_response_analysis", {}).get("mitigation_mentioned"),
                    "mitigation_effectiveness": final_state.get("risk_response_analysis", {}).get("mitigation_effectiveness"),
                    "mitigation_time_horizon": final_state.get("risk_response_analysis", {}).get("mitigation_time_horizon"),
                    "mitigation_actions": final_state.get("risk_response_analysis", {}).get("mitigation_actions"),
                    "mitigation_summary": fix_quotes(final_state.get("risk_response_analysis", {}).get("mitigation_summary")),
                    "transcript_sha256": final_state.get("transcript_sha256"),
                }
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    print(f"Failed to process {tic} after multiple retries: {e}")
                    raise e
                print(f"Error processing {tic}: {e}. Retrying...")
                

        processed_data.append(out)

    # Load processed data into core.earnings_transcript_analysis
    total_records = 0
    if conn:
        df = pd.DataFrame(processed_data)
        # Convert JSON array strings to Python lists for array columns
        array_cols = [
            "performance_factors", "growth_drivers", "risk_factors", "mitigation_actions"
        ]
        
        for col in array_cols:
            if col in df.columns:
                df[col] = df[col].astype(object)
                df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
        total_records = insert_records(conn, df, "core.earnings_transcript_analysis", ["tic", "calendar_year", "calendar_quarter"])
        conn.close()

    # End timing
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Inserted/Updated {total_records} records in {elapsed:.2f} seconds.")
    print(f"Total number of records is {len(processed_data)}.")

    # Adaptive rate limiting: sleep only for the remaining time up to the target interval
    if sleep_time is not None:
        remaining = max(0, sleep_time - elapsed)
        if remaining > 0:
            print(f"Rate limiting: sleeping {remaining:.0f}s (elapsed {elapsed:.1f}s, target {target_interval}s)")
            time.sleep(remaining)

if __name__ == "__main__":
    conn = connect_to_db()
    sleep_time = 125  # seconds to sleep between runs to avoid rate limits
    batch_size = 10  # number of companies to process before sleeping
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for i, record in enumerate(records):
            tic = record[0]
            print(f"\nProcessing {tic} ({i+1}/{len(records)})")
            main(tic=tic, calendar_year=None, calendar_quarter=None, sleep_time=sleep_time)
            # main(tic=tic, calendar_year=2024, calendar_quarter=4)
            # main(tic=tic, calendar_year=2025, calendar_quarter=1)
            # main(tic=tic, calendar_year=2025, calendar_quarter=2)
            # main(tic=tic, calendar_year=2025, calendar_quarter=3)
            # main(tic=tic, calendar_year=2025, calendar_quarter=4)
            if i > 0 and i % batch_size == 0:
                print(f"\n[Rate Limit Protection] Processed {batch_size} items. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
        conn.close()
