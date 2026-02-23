
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
import os
app_env = os.getenv("APP_ENV", "local")


def read_records(tic):
    """
    Reads data from the core.efficiency_metrics table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT
            e.inference_id,
            e.tic,
            e.date,
            -- final score
            ss.efficiency_score AS score,

            -- efficiency
            e.asset_turnover,
            e.fixed_asset_turnover,
            e.opex_ratio,
            e.cash_conversion_cycle,
            e.dso,
            e.dio,
            e.dpo,
            e.revenue_per_employee,

            -- efficiency percentiles
            ep.asset_turnover_percentile,
            ep.cash_conversion_cycle_percentile,
            ep.dso_percentile,
            ep.dio_percentile,
            ep.dpo_percentile,
            ep.fixed_asset_turnover_percentile,
            ep.revenue_per_employee_percentile,
            ep.opex_ratio_percentile,
            e.updated_at
        FROM core.efficiency_metrics e
        JOIN core.efficiency_percentiles ep
        ON e.inference_id = ep.inference_id
        JOIN core.stock_scores ss
        ON e.tic = ss.tic AND e.date = ss.date
        WHERE e.tic = '{tic}'
        ORDER BY e.date DESC
        LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for efficiency metrics.
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
            total_deleted = delete_published_records(conn_local, "mart.efficiency_metrics", today, commit=False)
            if app_env == "local":
                delete_published_records(conn_supabase, "mart.efficiency_metrics", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.efficiency_metrics for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['inference_id', 'tic', 'date', 'score', 
                        'asset_turnover', 'fixed_asset_turnover', 'opex_ratio', 'cash_conversion_cycle',
                        'dso', 'dio', 'dpo', 'revenue_per_employee',
                        'asset_turnover_percentile', 'cash_conversion_cycle_percentile',
                        'dso_percentile', 'dio_percentile', 'dpo_percentile',
                        'fixed_asset_turnover_percentile', 'revenue_per_employee_percentile',
                        'opex_ratio_percentile', 
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.efficiency_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                if app_env == "local":
                    insert_records(conn_supabase, df, "mart.efficiency_metrics", 
                                                ["tic", "date", "as_of_date"], 
                                                updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing efficiency metrics data: {e}")
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