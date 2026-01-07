
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



def read_records(tic):
    """
    Reads data from the core.growth_metrics table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT
        g.inference_id,
        g.tic,
        g.date,
        -- final score
        ss.growth_score AS score,

        -- growth
        g.revenue_growth_yoy,
        g.eps_growth_yoy,
        g.ebitda_growth_yoy,
        g.fcf_growth_yoy,
        
        
        g.revenue_cagr_3y,
        g.eps_cagr_3y,
        g.ebitda_cagr_3y,
        g.fcf_cagr_3y,
        
        g.operating_income_growth_yoy,
        g.forward_revenue_growth,
        g.forward_eps_growth,

        g.revenue_cagr_5y,
        g.eps_cagr_5y,
        g.ebitda_cagr_5y,
        g.fcf_cagr_5y,
        


        -- growth percentiles
        gp.revenue_growth_yoy_percentile,
        gp.revenue_cagr_3y_percentile,
        gp.eps_growth_yoy_percentile,
        gp.eps_cagr_3y_percentile,
        gp.fcf_growth_yoy_percentile,
        gp.fcf_cagr_3y_percentile,
        gp.ebitda_growth_yoy_percentile,
        gp.ebitda_cagr_3y_percentile,

        gp.revenue_cagr_5y_percentile,
        gp.eps_cagr_5y_percentile,
        gp.fcf_cagr_5y_percentile,
        gp.ebitda_cagr_5y_percentile,
        
        gp.operating_income_growth_yoy_percentile,
        gp.forward_revenue_growth_percentile,
        gp.forward_eps_growth_percentile,

        g.updated_at

    FROM core.growth_metrics g
    JOIN core.growth_percentiles gp
      ON g.inference_id = gp.inference_id
    JOIN core.stock_scores ss
      ON g.tic = ss.tic AND g.date = ss.date
    WHERE g.tic = '{tic}'
    ORDER BY g.date DESC
    LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for growth metrics.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.growth_metrics", today, commit=False)
            delete_published_records(conn_supabase, "mart.growth_metrics", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.growth_metrics for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['inference_id', 'tic', 'date', 'score', 
                        'revenue_growth_yoy', 'eps_growth_yoy', 'ebitda_growth_yoy', 'fcf_growth_yoy',
                        'revenue_cagr_3y', 'eps_cagr_3y', 'ebitda_cagr_3y', 'fcf_cagr_3y',
                        'operating_income_growth_yoy', 'forward_revenue_growth', 'forward_eps_growth',
                        'revenue_cagr_5y', 'eps_cagr_5y', 'ebitda_cagr_5y', 'fcf_cagr_5y',
                        'revenue_growth_yoy_percentile', 'revenue_cagr_3y_percentile',
                        'eps_growth_yoy_percentile', 'eps_cagr_3y_percentile',
                        'fcf_growth_yoy_percentile', 'fcf_cagr_3y_percentile',
                        'ebitda_growth_yoy_percentile', 'ebitda_cagr_3y_percentile',
                        'revenue_cagr_5y_percentile', 'eps_cagr_5y_percentile',
                        'fcf_cagr_5y_percentile', 'ebitda_cagr_5y_percentile',
                        'operating_income_growth_yoy_percentile', 'forward_revenue_growth_percentile',
                        'forward_eps_growth_percentile',
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.growth_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                insert_records(conn_supabase, df, "mart.growth_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing growth metrics data: {e}")
            conn_local.rollback()
            conn_supabase.rollback()
            conn_local.close()
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