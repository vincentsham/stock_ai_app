import time
import pandas as pd
from server.database.utils import connect_to_db
from states import CompanyProfileState
from graph import create_graph
from tqdm import tqdm

def insert_records(data, conn):
    """Insert processed data into core.stock_metadata."""
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute("""
                    INSERT INTO core.stock_metadata (
                        tic, name, sector, industry, country, market_cap, employees, exchange, currency, website, description, summary, short_summary, last_updated
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                    ON CONFLICT (tic) DO UPDATE SET
                        name = EXCLUDED.name,
                        sector = EXCLUDED.sector,
                        industry = EXCLUDED.industry,
                        country = EXCLUDED.country,
                        market_cap = EXCLUDED.market_cap,
                        employees = EXCLUDED.employees,
                        exchange = EXCLUDED.exchange,
                        currency = EXCLUDED.currency,
                        website = EXCLUDED.website,
                        description = EXCLUDED.description,
                        summary = EXCLUDED.summary,
                        short_summary = EXCLUDED.short_summary,
                        last_updated = NOW();
                """, (
                    record.get("tic"),
                    record.get("company_name"),
                    record.get("sector"),
                    record.get("industry"),
                    record.get("country"),
                    record.get("market_cap"),
                    record.get("employees"),
                    record.get("exchange"),
                    record.get("currency"),
                    record.get("website"),
                    record.get("description"),
                    record.get("summary"),
                    record.get("short_summary")
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
            SELECT tic, name, sector, industry, country, market_cap, employees, exchange, currency, website, description
            FROM raw.stock_metadata;
        """
        df = pd.read_sql_query(query, conn)
    else:
        print("Could not connect to database.")
        return

    # Construct states from the retrieved records
    states = [
        CompanyProfileState(
            tic=row['tic'],
            company_name=row['name'],
            sector=row['sector'],
            industry=row['industry'],
            country=row['country'],
            market_cap=row['market_cap'],
            employees=row['employees'],
            exchange=row['exchange'],
            currency=row['currency'],
            website=row['website'],
            description=row['description']
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