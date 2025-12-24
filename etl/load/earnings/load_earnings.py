import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import read_earnings_calendar, fuzzy_lookup_earnings_calendar
import json



def read_records(tic):
    """
    Reads data from the raw.earnings table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT 
        tic,
        earnings_date,
        fiscal_date,
        session,
        eps,
        eps_estimated,
        revenue,
        revenue_estimated,
        source,
        raw_json,
        raw_json_sha256
    FROM raw.earnings r
    WHERE tic = '{tic}';
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
        total_inserted = insert_records(conn, df, "core.earnings", 
                                        ["tic", "calendar_year", "calendar_quarter"], where=["raw_json_sha256"])

    # Close the database connection
    return total_inserted

def main():
    """
    Main function to orchestrate the ETL process for earnings.
    """
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            earnings_df = read_records(tic)
            calendar_df = read_earnings_calendar(tic)
            earliest_date = calendar_df['earnings_date'].min()
            earnings_df = earnings_df[pd.to_datetime(earnings_df['earnings_date']) >= pd.to_datetime(earliest_date) - pd.Timedelta(days=20)]
            cols = ['tic', 'calendar_year', 'calendar_quarter', 'earnings_date', 
                           'fiscal_year', 'fiscal_quarter', 'fiscal_date', 'session',
                           'eps', 'eps_estimated', 'revenue', 'revenue_estimated',
                           'source', 'raw_json', 'raw_json_sha256'
                           ]
            earnings_df = fuzzy_lookup_earnings_calendar(tic, earnings_df, calendar_df, cols)
            earnings_df['raw_json'] = earnings_df['raw_json'].apply(lambda x: json.dumps(x) if pd.notnull(x) else None)
            total_records = load_records(earnings_df)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()


if __name__ == "__main__":
    main()