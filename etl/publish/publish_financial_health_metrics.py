
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
import os
app_env = os.getenv("APP_ENV", "local")


def read_records(tic):
    """
    Reads data from the core.financial_health_metrics table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT
            fh.inference_id,
            fh.tic,
            fh.date,
            -- final score
            ss.financial_health_score AS score,

            -- financial health
            fh.net_debt_to_ebitda_ttm,
            fh.interest_coverage_ttm,
            fh.current_ratio,
            fh.quick_ratio,
            fh.cash_ratio,
            fh.debt_to_equity,
            fh.debt_to_assets,
            fh.altman_z_score,

            -- financial health percentiles
            fhp.net_debt_to_ebitda_ttm_percentile,
            fhp.interest_coverage_ttm_percentile,
            fhp.current_ratio_percentile,
            fhp.quick_ratio_percentile,
            fhp.cash_ratio_percentile,
            fhp.debt_to_equity_percentile,
            fhp.debt_to_assets_percentile,
            fhp.altman_z_score_percentile,
            fh.updated_at
        FROM core.financial_health_metrics fh
        JOIN core.financial_health_percentiles fhp
        ON fh.inference_id = fhp.inference_id
        JOIN core.stock_scores ss
        ON fh.tic = ss.tic AND fh.date = ss.date
        WHERE fh.tic = '{tic}'
        ORDER BY fh.date DESC
        LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for financial health metrics.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.financial_health_metrics", today, commit=False)
            delete_published_records(conn_supabase, "mart.financial_health_metrics", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.financial_health_metrics for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['inference_id', 'tic', 'date', 'score', 
                        'net_debt_to_ebitda_ttm', 'interest_coverage_ttm', 'current_ratio',
                        'quick_ratio', 'cash_ratio', 'debt_to_equity', 'debt_to_assets', 'altman_z_score',
                        'net_debt_to_ebitda_ttm_percentile', 'interest_coverage_ttm_percentile', 'current_ratio_percentile',
                        'quick_ratio_percentile', 'cash_ratio_percentile', 'debt_to_equity_percentile', 
                        'debt_to_assets_percentile', 'altman_z_score_percentile',
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.financial_health_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                insert_records(conn_supabase, df, "mart.financial_health_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing financial health metrics data: {e}")
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