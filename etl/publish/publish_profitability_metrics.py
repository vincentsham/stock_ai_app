
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



def read_records(tic):
    """
    Reads data from the core.profitability_metrics table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT
            p.inference_id,
            p.tic,
            p.date,
            -- final score
            ss.profitability_score AS score,

            -- profitability
            p.net_margin,
            p.operating_margin,
            p.gross_margin,
            p.ebitda_margin,

            p.roa,
            p.roe,
            p.roic,
            p.ocf_margin,
            p.fcf_margin,

            -- profitability percentiles
            pp.gross_margin_percentile,
            pp.operating_margin_percentile,
            pp.ebitda_margin_percentile,
            pp.net_margin_percentile,
            pp.roe_percentile,
            pp.roa_percentile,
            pp.roic_percentile,
            pp.ocf_margin_percentile,
            pp.fcf_margin_percentile,

            p.updated_at

        FROM core.profitability_metrics p
        JOIN core.profitability_percentiles pp
        ON p.inference_id = pp.inference_id
        JOIN core.stock_scores ss
        ON p.tic = ss.tic AND p.date = ss.date
        WHERE p.tic = '{tic}'
        ORDER BY p.date DESC
        LIMIT 1;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for profitability metrics.
    """
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn, "mart.profitability_metrics", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.profitability_metrics for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['inference_id', 'tic', 'date', 'score', 
                        'net_margin', 'operating_margin', 'gross_margin', 'ebitda_margin',
                        'roa', 'roe', 'roic', 'ocf_margin', 'fcf_margin',
                        'gross_margin_percentile', 'operating_margin_percentile',
                        'ebitda_margin_percentile', 'net_margin_percentile',
                        'roe_percentile', 'roa_percentile', 'roic_percentile',
                        'ocf_margin_percentile', 'fcf_margin_percentile',
                        'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn, df, "mart.profitability_metrics", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing profitability metrics data: {e}")
            conn.rollback()
            conn.close()
            return
        conn.commit()
        conn.close()
        return
    return


if __name__ == "__main__":
    main()