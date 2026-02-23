
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
        WITH latest_earnings AS (
            SELECT 
                tic, calendar_year, calendar_quarter, earnings_date,
                eps, eps_estimated, revenue, revenue_estimated
            FROM core.earnings 
            WHERE tic = '{tic}' AND eps IS NOT NULL 
            ORDER BY tic, calendar_year DESC, calendar_quarter DESC 
        LIMIT 1)
        SELECT 
            le.tic, 
            le.calendar_year, 
            le.calendar_quarter,
            le.earnings_date,
            em.eps_surprise_regime, 
            em.revenue_surprise_regime,
            edm.eps_diluted_yoy_growth_regime AS eps_yoy_growth_regime, 
            edm.eps_diluted_yoy_accel_regime AS  eps_yoy_accel_regime,
            rm.revenue_yoy_growth_regime AS revenue_yoy_growth_regime, 
            rm.revenue_yoy_accel_regime AS revenue_yoy_accel_regime,
            em.updated_at
        FROM latest_earnings le
        JOIN core.earnings_metrics em
        ON em.tic = le.tic
        AND em.calendar_year = le.calendar_year
        AND em.calendar_quarter = le.calendar_quarter
        JOIN core.eps_diluted_metrics edm
        ON edm.tic = le.tic
        AND edm.calendar_year = le.calendar_year
        AND edm.calendar_quarter = le.calendar_quarter
        JOIN core.revenue_metrics rm
        ON rm.tic = le.tic
        AND rm.calendar_year = le.calendar_year
        AND rm.calendar_quarter = le.calendar_quarter
        WHERE le.tic = '{tic}'
    ;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for earnings regime.
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
            total_deleted = delete_published_records(conn_local, "mart.earnings_regime", today, commit=False)
            if app_env == "local":
                delete_published_records(conn_supabase, "mart.earnings_regime", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.earnings_regime for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['tic', 'calendar_year', 'calendar_quarter', 'earnings_date', 
                        'eps_surprise_regime', 'revenue_surprise_regime',
                        'eps_yoy_growth_regime', 'eps_yoy_accel_regime',
                        'revenue_yoy_growth_regime', 'revenue_yoy_accel_regime',
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.earnings_regime", 
                                            ["tic", "calendar_year", "calendar_quarter", "as_of_date"], 
                                            updated_at=False, commit=False)
                if app_env == "local":
                    insert_records(conn_supabase, df, "mart.earnings_regime", 
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