
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



def read_records(tic):
    """
    Reads data from the core.valuation_metrics table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT
        v.inference_id,
        v.tic,
        v.date,
        ss.valuation_score AS score,

        -- valuation
        v.pe_ttm,
        v.pe_forward,
        v.ps_ttm,
        v.peg_ratio,
        v.peg_ratio_forward,
        v.p_to_fcf_ttm,
        v.price_to_book,

        v.ev_to_revenue_ttm,
        v.ev_to_ebitda_ttm,
        v.ev_to_fcf_ttm,

        v.earnings_yield_ttm,
        v.revenue_yield_ttm,
        v.fcf_yield_ttm,
        v.total_shareholder_yield_ttm,

        -- valuation percentiles
        vp.pe_ttm_percentile,
        vp.pe_forward_percentile,
        vp.ps_ttm_percentile,
        vp.peg_ratio_percentile,
        vp.peg_ratio_forward_percentile,
        vp.p_to_fcf_ttm_percentile,
        vp.price_to_book_percentile,

        vp.ev_to_revenue_ttm_percentile,
        vp.ev_to_ebitda_ttm_percentile,
        vp.ev_to_fcf_ttm_percentile,

        vp.fcf_yield_ttm_percentile,
        vp.earnings_yield_ttm_percentile,
        vp.revenue_yield_ttm_percentile,
        vp.total_shareholder_yield_ttm_percentile,
        v.updated_at

        FROM core.valuation_metrics v
        JOIN core.valuation_percentiles vp
        ON v.inference_id = vp.inference_id
        JOIN core.stock_scores ss
        ON v.tic = ss.tic AND v.date = ss.date
        WHERE v.tic = '{tic}'
        ORDER BY v.date DESC
        LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for valuation metrics.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.valuation_metrics", today, commit=False)
            delete_published_records(conn_supabase, "mart.valuation_metrics", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.valuation_metrics for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['inference_id', 'tic', 'date', 'score', 
                        'pe_ttm', 'pe_forward', 'ps_ttm', 'peg_ratio', 'peg_ratio_forward', 
                        'p_to_fcf_ttm', 'price_to_book',
                        'ev_to_revenue_ttm', 'ev_to_ebitda_ttm', 'ev_to_fcf_ttm',
                        'earnings_yield_ttm', 'revenue_yield_ttm', 'fcf_yield_ttm', 'total_shareholder_yield_ttm',
                        'pe_ttm_percentile', 'pe_forward_percentile', 'ps_ttm_percentile', 
                        'peg_ratio_percentile', 'peg_ratio_forward_percentile',
                        'p_to_fcf_ttm_percentile', 'price_to_book_percentile',
                        'ev_to_revenue_ttm_percentile', 'ev_to_ebitda_ttm_percentile', 'ev_to_fcf_ttm_percentile',
                        'fcf_yield_ttm_percentile', 'earnings_yield_ttm_percentile', 'revenue_yield_ttm_percentile',
                        'total_shareholder_yield_ttm_percentile',
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.valuation_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                insert_records(conn_supabase, df, "mart.valuation_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing valuation metrics data: {e}")
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