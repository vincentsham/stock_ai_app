import time
import pandas as pd
from server.database.utils import connect_to_db, insert_records
from states import merged_state_factory, MergedState
from graph import create_graph
from tqdm import tqdm
from etl_pipeline.utils import read_sql_query  # Import the custom read_sql_query function



def main():
    """Main function to execute the stock profile summarization pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = """
            SELECT et.tic, sm.name, sm.sector, sm.industry, sm.short_summary, 
                   et.calendar_year, et.calendar_quarter, et.earnings_date, et.transcript_sha256
            FROM core.earnings_transcripts AS et
            JOIN core.stock_profiles AS sm 
            ON et.tic = sm.tic;
        """
        df = read_sql_query(query, conn)
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
        ), row['transcript_sha256'])
        for _, row in df.iterrows()
    ]


    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    processed_data = []

    # Use tqdm to track progress
    for state in tqdm(states, desc="Processing company profiles"):
        final_state = app.invoke(state[0])
        final_state['transcript_sha256'] = state[1]  # Add transcript_sha256 to the final state
        out = {  
                    "tic": final_state.get("company_info", {}).get("tic"),
                    "calendar_year": final_state.get("company_info", {}).get("calendar_year"),
                    "calendar_quarter": final_state.get("company_info", {}).get("calendar_quarter"),
                    "sentiment": final_state.get("past_analysis", {}).get("sentiment"),
                    "durability": final_state.get("past_analysis", {}).get("durability"),
                    "performance_factors": final_state.get("past_analysis", {}).get("performance_factors"),
                    "past_summary": final_state.get("past_analysis", {}).get("past_summary"),
                    "guidance_direction": final_state.get("future_analysis", {}).get("guidance_direction"),
                    "revenue_outlook": final_state.get("future_analysis", {}).get("revenue_outlook"),
                    "margin_outlook": final_state.get("future_analysis", {}).get("margin_outlook"),
                    "earnings_outlook": final_state.get("future_analysis", {}).get("earnings_outlook"),
                    "cashflow_outlook": final_state.get("future_analysis", {}).get("cashflow_outlook"),
                    "growth_acceleration": final_state.get("future_analysis", {}).get("growth_acceleration"),
                    "future_outlook_sentiment": final_state.get("future_analysis", {}).get("sentiment"),
                    "catalysts": final_state.get("future_analysis", {}).get("catalysts"),
                    "future_summary": final_state.get("future_analysis", {}).get("future_summary"),
                    "risk_mentioned": final_state.get("risk_analysis", {}).get("risk_mentioned"),
                    "risk_impact": final_state.get("risk_analysis", {}).get("risk_impact"),
                    "risk_time_horizon": final_state.get("risk_analysis", {}).get("risk_time_horizon"),
                    "risk_factors": final_state.get("risk_analysis", {}).get("risk_factors"),
                    "risk_summary": final_state.get("risk_analysis", {}).get("risk_summary"),
                    "mitigation_mentioned": final_state.get("risk_response_analysis", {}).get("mitigation_mentioned"),
                    "mitigation_effectiveness": final_state.get("risk_response_analysis", {}).get("mitigation_effectiveness"),
                    "mitigation_time_horizon": final_state.get("risk_response_analysis", {}).get("mitigation_time_horizon"),
                    "mitigation_actions": final_state.get("risk_response_analysis", {}).get("mitigation_actions"),
                    "mitigation_summary": final_state.get("risk_response_analysis", {}).get("mitigation_summary"),
                    "transcript_sha256": final_state.get("transcript_sha256"),
        }
        processed_data.append(out)

    # Load processed data into core.stock_metadata
    total_records = 0
    if conn:
        df = pd.DataFrame(processed_data)
        total_records = insert_records(conn, df, "core.earnings_transcript_analysis", ["tic", "calendar_year", "calendar_quarter"])
        conn.close()

    # End timing
    end_time = time.time()
    print(f"Inserted/Updated {total_records} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of records is {len(processed_data)}.")

if __name__ == "__main__":
    main()