import time
import pandas as pd
from database.utils import connect_to_db, read_sql_query, insert_records
from states import CompanyProfileState
from graph import create_graph
from tqdm import tqdm



def main():
    """Main function to execute the stock profile summarization pipeline."""
    # Connect to the database
    conn = connect_to_db()
    if conn:
        query = """
            WITH latest_raw AS (
                SELECT DISTINCT ON (tic)
                        tic, name, sector, industry, country, market_cap, employees,
                        description, website, exchange, currency, raw_json_sha256, updated_at
                FROM raw.stock_profiles
                ORDER BY tic, updated_at DESC
            )
            SELECT r.tic, r.name, r.sector, r.industry, r.country, 
                   r.market_cap, r.employees, r.exchange, r.currency, 
                   r.website, r.description, r.raw_json_sha256
            FROM latest_raw r
            LEFT JOIN core.stock_profiles c USING (tic)
            WHERE c.tic IS NULL
                OR c.raw_json_sha256 IS DISTINCT FROM r.raw_json_sha256;
        """
        df = read_sql_query(query, conn)
        
    else:
        print("Could not connect to database.")
        return

    # Construct states from the retrieved records
    states = [
        (CompanyProfileState(
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
        ), 
        row['raw_json_sha256'])
        for _, row in df.iterrows()
    ]

    # Create and compile the graph
    graph = create_graph()
    app = graph.compile()

    # Start timing
    start_time = time.time()
    processed_data = []
    retries = 3

    # Use tqdm to track progress
    for state in tqdm(states, desc="Processing company profiles"):
        while retries > 0:
            try:
                final_state = app.invoke(state[0])
                retries = 3  # reset retries for next state
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    print(f"Failed to process {state[0].tic} after multiple retries: {e}")
                    raise e
                print(f"Error processing {state[0].tic}: {e}. Retrying...")

        final_state['raw_json_sha256'] = state[1]  # retain raw_json_sha256 for integrity
        processed_data.append(final_state)

    # Load processed data into core.stock_metadata
    total_records = 0
    if conn:
        processed_data = pd.DataFrame(processed_data)
        processed_data = processed_data[["tic","company_name","sector","industry","country",
                                         "market_cap","employees","exchange","currency",
                                         "website","description","summary","short_summary",
                                         "raw_json_sha256"]]
        total_records = insert_records(conn, processed_data, 'core.stock_profiles', ['tic'])
        

        conn.close()

    # End timing
    end_time = time.time()
    print(f"Processed {len(states)} records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of records is {total_records}.")

if __name__ == "__main__":
    main()