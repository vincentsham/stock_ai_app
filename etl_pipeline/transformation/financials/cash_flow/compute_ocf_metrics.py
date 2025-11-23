from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
from etl_pipeline.transformation.financials.gsa_framework.compute_growth_metrics import compute_growth_metrics 
from etl_pipeline.transformation.financials.gsa_framework.compute_stability_metrics import compute_stability_metrics
from etl_pipeline.transformation.financials.gsa_framework.compute_accel_metrics import compute_accel_metrics 
import pandas as pd

def read_records(conn, tic: str) -> pd.DataFrame:
    query = f"""
        SELECT c.event_id, c.tic, c.calendar_year, c.calendar_quarter, c.operating_cash_flow AS ocf, c.raw_json_sha256
        FROM core.cash_flow_statements as c
        LEFT JOIN core.ocf_metrics as r 
        ON c.tic = r.tic
            AND c.calendar_year = r.calendar_year
            AND c.calendar_quarter = r.calendar_quarter
        WHERE c.tic = '{tic}'
            AND (r.raw_json_sha256 IS NULL OR r.raw_json_sha256 <> c.raw_json_sha256)
        ORDER BY c.tic, c.calendar_year, c.calendar_quarter;
    """
    df = read_sql_query(query, conn)
    print(f"Records to process: {len(df)}")
    return df


def transform_records(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = df.copy()
    transformed_df['ocf_ttm'] = transformed_df['ocf'].rolling(window=4).sum()
    transformed_df = compute_growth_metrics(transformed_df, column="ocf", score_regime=[-0.1, 0, 0.1, 0.3])
    transformed_df = compute_stability_metrics(transformed_df, column="ocf", volatility_threshold=0.1)
    transformed_df = compute_accel_metrics(transformed_df, column="ocf")
    return transformed_df


def load_records(transformed_df, conn):

    # Insert records into core.ocf_metrics
    total_records = insert_records(conn, transformed_df, 'core.ocf_metrics', ['tic', 'calendar_year', 'calendar_quarter'])
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
