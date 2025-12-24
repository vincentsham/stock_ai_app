
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



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
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn, "mart.stock_scores", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.stock_scores for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['tic', 'date', 'valuation_score', 'profitability_score', 'growth_score', 'efficiency_score',
                        'financial_health_score', 'total_score', 'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn, df, "mart.stock_scores", 
                                            ["tic", "date", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing stock scores data: {e}")
            conn.rollback()
            conn.close()
            return
        conn.commit()
        conn.close()
        return
    return


if __name__ == "__main__":
    main()