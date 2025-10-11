import time
import pandas as pd
from server.database.utils import connect_to_db
from states import merged_state_factory, MergedState
from graph import create_graph
from tqdm import tqdm

def insert_records(data, conn):
    """Insert processed data into core.earnings_transcript_analysis."""
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute("""
                    INSERT INTO core.earnings_transcript_analysis (
                        tic, fiscal_year, fiscal_quarter,
                        sentiment, durability, performance_factors, past_summary,
                        guidance_direction, revenue_outlook, margin_outlook, earnings_outlook, cashflow_outlook, growth_acceleration, future_outlook_sentiment, catalysts, future_summary,
                        risk_mentioned, risk_impact, risk_time_horizon, risk_factors, risk_summary,
                        mitigation_mentioned, mitigation_effectiveness, mitigation_time_horizon, mitigation_actions, mitigation_summary,
                        last_updated
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        NOW()
                    )
                    ON CONFLICT (tic, fiscal_year, fiscal_quarter) DO UPDATE SET
                        sentiment = EXCLUDED.sentiment,
                        durability = EXCLUDED.durability,
                        performance_factors = EXCLUDED.performance_factors,
                        past_summary = EXCLUDED.past_summary,
                        guidance_direction = EXCLUDED.guidance_direction,
                        revenue_outlook = EXCLUDED.revenue_outlook,
                        margin_outlook = EXCLUDED.margin_outlook,
                        earnings_outlook = EXCLUDED.earnings_outlook,
                        cashflow_outlook = EXCLUDED.cashflow_outlook,
                        growth_acceleration = EXCLUDED.growth_acceleration,
                        future_outlook_sentiment = EXCLUDED.future_outlook_sentiment,
                        catalysts = EXCLUDED.catalysts,
                        future_summary = EXCLUDED.future_summary,
                        risk_mentioned = EXCLUDED.risk_mentioned,
                        risk_impact = EXCLUDED.risk_impact,
                        risk_time_horizon = EXCLUDED.risk_time_horizon,
                        risk_factors = EXCLUDED.risk_factors,
                        risk_summary = EXCLUDED.risk_summary,
                        mitigation_mentioned = EXCLUDED.mitigation_mentioned,
                        mitigation_effectiveness = EXCLUDED.mitigation_effectiveness,
                        mitigation_time_horizon = EXCLUDED.mitigation_time_horizon,
                        mitigation_actions = EXCLUDED.mitigation_actions,
                        mitigation_summary = EXCLUDED.mitigation_summary,
                        last_updated = NOW();
                """,
                (
                    record.get("company_info", {}).get("tic"),
                    record.get("company_info", {}).get("fiscal_year"),
                    record.get("company_info", {}).get("fiscal_quarter"),
                    record.get("past_analysis", {}).get("sentiment"),
                    record.get("past_analysis", {}).get("durability"),
                    record.get("past_analysis", {}).get("performance_factors"),
                    record.get("past_analysis", {}).get("past_summary"),
                    record.get("future_analysis", {}).get("guidance_direction"),
                    record.get("future_analysis", {}).get("revenue_outlook"),
                    record.get("future_analysis", {}).get("margin_outlook"),
                    record.get("future_analysis", {}).get("earnings_outlook"),
                    record.get("future_analysis", {}).get("cashflow_outlook"),
                    record.get("future_analysis", {}).get("growth_acceleration"),
                    record.get("future_analysis", {}).get("sentiment"),
                    record.get("future_analysis", {}).get("catalysts"),
                    record.get("future_analysis", {}).get("future_summary"),
                    record.get("risk_analysis", {}).get("risk_mentioned"),
                    record.get("risk_analysis", {}).get("risk_impact"),
                    record.get("risk_analysis", {}).get("risk_time_horizon"),
                    record.get("risk_analysis", {}).get("risk_factors"),
                    record.get("risk_analysis", {}).get("risk_summary"),
                    record.get("risk_response_analysis", {}).get("mitigation_mentioned"),
                    record.get("risk_response_analysis", {}).get("mitigation_effectiveness"),
                    record.get("risk_response_analysis", {}).get("mitigation_time_horizon"),
                    record.get("risk_response_analysis", {}).get("mitigation_actions"),
                    record.get("risk_response_analysis", {}).get("mitigation_summary")
                ))
            conn.commit()
    except Exception as e:
        print(f"Error inserting analysis data: {e}")
        conn.rollback()

def main():
    """Main function to execute the stock profile summarization pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = """
            SELECT et.tic, sm.name, sm.sector, sm.industry, sm.short_summary, et.fiscal_year, et.fiscal_quarter, et.earnings_date
            FROM raw.earnings_transcripts et
            LEFT JOIN core.stock_metadata sm ON et.tic = sm.tic;
        """
        df = pd.read_sql_query(query, conn)
    else:
        print("Could not connect to database.")
        return



    # Construct states from the retrieved records
    states = [
        merged_state_factory(
            tic=row['tic'],
            company_name=row['name'],
            sector=row['sector'],
            industry=row['industry'],
            company_description=row['short_summary'],
            fiscal_year=row['fiscal_year'],
            fiscal_quarter=row['fiscal_quarter'],
            earnings_date=row['earnings_date'].isoformat()
        )
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
        final_state = app.invoke(state)
        processed_data.append(final_state)

    # Load processed data into core.stock_metadata
    if conn:
        insert_records(processed_data, conn)
        conn.close()

    # End timing
    end_time = time.time()
    print(f"Processed {len(states)} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of records is {len(processed_data)}.")

if __name__ == "__main__":
    main()