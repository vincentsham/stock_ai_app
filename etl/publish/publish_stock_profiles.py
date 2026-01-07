
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
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.stock_profiles", today, commit=False)
            delete_published_records(conn_supabase, "mart.stock_profiles", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.stock_profiles for as_of_date = {today}")
            df = read_records()
            df['as_of_date'] = today
            cols = ['tic', 'name', 'exchange', 'sector', 'industry',
                    'updated_at', 'as_of_date' 
                    ]
            df = df[cols]
            total_inserted = insert_records(conn_local, df, "mart.stock_profiles", 
                                        ["tic", "as_of_date"], 
                                        updated_at=False, commit=False,
                                        batch_size=10)
            insert_records(conn_supabase, df, "mart.stock_profiles", 
                                        ["tic", "as_of_date"],
                                        updated_at=False, commit=False,
                                        batch_size=10)
            print(f"Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing earnings data: {e}")
            conn_local.rollback()
            conn_local.close()
            conn_supabase.rollback()
            conn_supabase.close()
            return
        conn_local.commit()
        conn_local.close()
        conn_supabase.commit()
        conn_supabase.close()
        return
    return


if __name__ == "__main__":
    main()