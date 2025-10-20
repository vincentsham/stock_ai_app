import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.earnings table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT 
        e.tic,
        c.calendar_year,
        c.calendar_quarter,
        e.earnings_date,
        c.fiscal_date,
        c.session,
        e.eps,
        e.eps_estimated,
        e.revenue,
        e.revenue_estimated,
        e.price_before,
        e.price_after,
        e.source,
        e.raw_json,
        e.raw_json_sha256
    FROM raw.earnings as e
    INNER JOIN core.earnings_calendar as c
    ON e.tic = c.tic AND e.earnings_date = c.earnings_date
    LEFT JOIN core.earnings as ce
    ON e.tic = ce.tic AND e.earnings_date = ce.earnings_date
    WHERE   e.earnings_date IS NOT NULL
            AND (ce.raw_json IS NULL OR e.raw_json_sha256 IS DISTINCT FROM ce.raw_json_sha256);
    """

    # Connect to the database
    df = execute_query(query)
    return df



def load_records(df):
    """
    Loads the transformed earnings data into the core.earnings table.
    """
    # Insert the transformed records into the database
    with connect_to_db() as conn:
        total_inserted = insert_records(conn, df, "core.earnings", ["tic", "calendar_year", "calendar_quarter"])
        print(f"Total records inserted: {total_inserted}")

    # Close the database connection
    return total_inserted

def main():
    """
    Main function to orchestrate the ETL process for earnings.
    """
    earnings_df = read_records()
    earnings_df['raw_json'] = earnings_df['raw_json'].apply(lambda x: json.dumps(x) if pd.notnull(x) else {})   

    load_records(earnings_df)

if __name__ == "__main__":
    main()