
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



def read_records():
    """
    Reads data from the core.stock_profiles table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT tic, name, exchange, sector, industry, updated_at
        FROM core.stock_profiles
    """

    # Connect to the database
    df = execute_query(query)
    return df


def main():
    """
    Main function to orchestrate the ETL process for stock profiles.
    """
    conn = connect_to_db()
    if conn:
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn, "mart.stock_profiles", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.stock_profiles for as_of_date = {today}")
            df = read_records()
            df['as_of_date'] = today
            cols = ['tic', 'name', 'exchange', 'sector', 'industry',
                    'updated_at', 'as_of_date' 
                    ]
            df = df[cols]
            total_inserted = insert_records(conn, df, "mart.stock_profiles", 
                                        ["tic", "as_of_date"], 
                                        updated_at=False, commit=False)
            print(f"Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing earnings data: {e}")
            conn.rollback()
            conn.close()
            return
        conn.commit()
        conn.close()
        return
    return


if __name__ == "__main__":
    main()