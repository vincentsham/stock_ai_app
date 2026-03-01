
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
import os
app_env = os.getenv("APP_ENV", "local")


def read_records(tic):
    """
    Reads data from the core.analyst_rating_yearly_summary table and returns it as a pandas DataFrame.
    """
    query = f"""
        WITH latest_date AS (
            SELECT date
            FROM raw.stock_ohlcv_daily
            WHERE tic = '{tic}'
            ORDER BY date DESC
            LIMIT 1
        )
        SELECT sod.tic,
            sod.date,
            sod.close,
            arqs.pt_count,
            arqs.pt_high,
            arqs.pt_low,
            arqs.pt_p25,
            arqs.pt_median,
            arqs.pt_p75,
            arqs.pt_upgrade_n,
            arqs.pt_downgrade_n,
            arqs.pt_reiterate_n,
            arqs.pt_init_n,
            arqs.grade_count,
            arqs.grade_buy_n,
            arqs.grade_hold_n,
            arqs.grade_sell_n,
            arqs.grade_upgrade_n,
            arqs.grade_downgrade_n,
            arqs.grade_reiterate_n,
            arqs.grade_init_n,
            arqs.updated_at
        FROM raw.stock_ohlcv_daily sod
        JOIN latest_date ld ON sod.date BETWEEN ld.date - INTERVAL '1 year' AND ld.date
        LEFT JOIN core.analyst_rating_yearly_summary arqs
            ON arqs.tic = sod.tic
            AND arqs.end_date = sod.date
        WHERE sod.tic = '{tic}'
            AND arqs.pt_count IS NOT NULL 
            AND arqs.grade_count IS NOT NULL
        ORDER BY sod.date DESC;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for analyst_rating_yearly_summary.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")

    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.analyst_rating_yearly_summary", today, commit=False)
            delete_published_records(conn_supabase, "mart.analyst_rating_yearly_summary", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.analyst_rating_yearly_summary for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['tic', 'date', 'close', 'pt_count', 'pt_high', 'pt_low', 'pt_p25',
                        'pt_median', 'pt_p75', 'pt_upgrade_n', 'pt_downgrade_n', 'pt_reiterate_n',
                        'pt_init_n', 'grade_count', 'grade_buy_n', 'grade_hold_n', 'grade_sell_n',
                        'grade_upgrade_n', 'grade_downgrade_n', 'grade_reiterate_n', 'grade_init_n',
                        'updated_at', 'as_of_date' 
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.analyst_rating_yearly_summary", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                insert_records(conn_supabase, df, "mart.analyst_rating_yearly_summary", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing analyst_rating_yearly_summary data: {e}")
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