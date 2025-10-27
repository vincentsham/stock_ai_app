from server.database.utils import connect_to_db, execute_query, insert_records, read_sql_query
from etl_pipeline.transformation.financials.gsa_framework.compute_growth_metrics import compute_growth_metrics 
from etl_pipeline.transformation.financials.gsa_framework.compute_stability_metrics import compute_stability_metrics
from etl_pipeline.transformation.financials.gsa_framework.compute_accel_metrics import compute_accel_metrics 
import pandas as pd

def read_records(conn, tic: str) -> pd.DataFrame:
    query = f"""
        SELECT e.event_id, e.tic, e.calendar_year, e.calendar_quarter, e.revenue, e.raw_json_sha256
        FROM core.earnings as e
        LEFT JOIN core.revenue_metrics as r 
        ON e.tic = r.tic
            AND e.calendar_year = r.calendar_year
            AND e.calendar_quarter = r.calendar_quarter
        WHERE e.tic = '{tic}'
            AND (r.raw_json_sha256 IS NULL OR r.raw_json_sha256 <> e.raw_json_sha256)
        ORDER BY e.tic, e.calendar_year, e.calendar_quarter;
    """
    df = read_sql_query(query, conn)
    print(f"Records to process: {len(df)}")
    return df


def transform_records(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = df.copy()
    transformed_df['revenue_ttm'] = transformed_df['revenue'].rolling(window=4).sum()
    transformed_df = compute_growth_metrics(transformed_df, column="revenue", score_regime=[-0.1, 0, 0.1, 0.3])
    transformed_df = compute_stability_metrics(transformed_df, column="revenue", volatility_threshold=0.05)
    transformed_df = compute_accel_metrics(transformed_df, column="revenue")
    return transformed_df


def load_records(transformed_df, conn):

    # Insert records into core.revenue_metrics
    total_records = insert_records(conn, transformed_df, 'core.revenue_metrics', ['tic', 'calendar_year', 'calendar_quarter'])
    return total_records

def main():
    # Connect to the database
    conn = connect_to_db()
    if conn is not None:
        # Extract records
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for record in records:
            df = read_records(conn, record[0])
            if df.empty:
                print("No new or updated records to process.")
                return
            transformed_df = transform_records(df)
            # Load records
            total_records = load_records(transformed_df, conn)
            print(f"Total records inserted/updated for {record[0]}: {total_records}")

    return


if __name__ == "__main__":
    main()
