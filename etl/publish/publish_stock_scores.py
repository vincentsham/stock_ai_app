
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
import os 

app_env = os.getenv("APP_ENV", "local")

def read_records(tic):
    """
    Reads data from the core.stock_scores table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT
      ss.tic,
      ss.date,
      ss.valuation_score,
      ss.profitability_score,
      ss.growth_score,
      ss.efficiency_score,
      ss.financial_health_score,
      ss.total_score,
      ss.updated_at
    FROM core.stock_scores ss
    WHERE ss.tic = '{tic}'
    ORDER BY ss.date DESC
    LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for stock scores.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = True 
    if app_env == "local":
        conn_supabase = connect_to_db("supabase")
         
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.stock_scores", today, commit=False)
            if app_env == "local":
                delete_published_records(conn_supabase, "mart.stock_scores", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.stock_scores for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['tic', 'date', 'valuation_score', 'profitability_score', 'growth_score', 'efficiency_score',
                        'financial_health_score', 'total_score', 'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.stock_scores", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                if app_env == "local":
                    insert_records(conn_supabase, df, "mart.stock_scores", 
                                                ["tic", "date", "as_of_date"], 
                                                updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing stock scores data: {e}")
            conn_local.rollback()
            conn_local.close()
            if app_env == "local":
                conn_supabase.rollback()
                conn_supabase.close()
            return
        conn_local.commit()
        conn_local.close()
        if app_env == "local":
            conn_supabase.commit()
            conn_supabase.close()
        return
    return


if __name__ == "__main__":
    main()