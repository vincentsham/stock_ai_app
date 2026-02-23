
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
import os
app_env = os.getenv("APP_ENV", "local")


def read_records(tic):
    """
    Reads data from the core.earnings table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT *
    FROM (
        SELECT e.tic, e.calendar_year, e.calendar_quarter, e.earnings_date, 
              e.eps, e.eps_estimated, 
              edm.eps_diluted_yoy_growth * 100 AS eps_yoy_growth,
              edm.eps_diluted_yoy_accel * 100 AS eps_yoy_acceleration,
              e.revenue, e.revenue_estimated, 
              rm.revenue_yoy_growth * 100 AS revenue_yoy_growth, 
              rm.revenue_yoy_accel * 100 AS revenue_yoy_acceleration,
              e.updated_at
        FROM core.earnings AS e
        LEFT JOIN core.eps_diluted_metrics AS edm
        ON e.tic = edm.tic 
          AND e.calendar_year = edm.calendar_year
          AND e.calendar_quarter = edm.calendar_quarter
        LEFT JOIN core.revenue_metrics AS rm
        ON e.tic = rm.tic
          AND e.calendar_year = rm.calendar_year
          AND e.calendar_quarter = rm.calendar_quarter
        WHERE e.tic = '{tic}' AND e.eps_estimated IS NOT NULL
        ORDER BY e.calendar_year DESC, e.calendar_quarter DESC
        LIMIT 10) AS subquery
    ORDER BY calendar_year ASC, calendar_quarter ASC;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for earnings.
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
            total_deleted = delete_published_records(conn_local, "mart.earnings", today, commit=False)
            if app_env == "local":
                delete_published_records(conn_supabase, "mart.earnings", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.earnings for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['tic', 'calendar_year', 'calendar_quarter', 'earnings_date', 
                        'eps', 'eps_estimated', 'eps_yoy_growth', 'eps_yoy_acceleration',
                        'revenue', 'revenue_estimated', 'revenue_yoy_growth', 'revenue_yoy_acceleration',
                        'updated_at', 'as_of_date' 
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.earnings", 
                                            ["tic", "calendar_year", "calendar_quarter", "as_of_date"], 
                                            updated_at=False, commit=False)
                if app_env == "local":
                    insert_records(conn_supabase, df, "mart.earnings", 
                                                ["tic", "calendar_year", "calendar_quarter", "as_of_date"], 
                                                updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing earnings data: {e}")
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