from server.database.utils import connect_to_db, execute_query, insert_records, read_sql_query
from etl_pipeline.transformation.financials.gsa_framework.compute_growth_metrics import compute_growth_metrics 
from etl_pipeline.transformation.financials.gsa_framework.compute_stability_metrics import compute_stability_metrics
from etl_pipeline.transformation.financials.gsa_framework.compute_accel_metrics import compute_accel_metrics 
import pandas as pd

def read_records(conn, tic: str) -> pd.DataFrame:
    query = f"""
        SELECT b.event_id, b.tic, b.calendar_year, b.calendar_quarter, b.ebit, b.interest_expense, b.raw_json_sha256
        FROM core.income_statements as b
        LEFT JOIN core.icr_metrics as r 
        ON b.tic = r.tic
            AND b.calendar_year = r.calendar_year
            AND b.calendar_quarter = r.calendar_quarter
        WHERE b.tic = '{tic}'
            AND (r.raw_json_sha256 IS NULL OR r.raw_json_sha256 <> b.raw_json_sha256)
        ORDER BY b.tic, b.calendar_year, b.calendar_quarter;
    """
    df = read_sql_query(query, conn)
    print(f"Records to process: {len(df)}")
    return df


def transform_records(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = df.copy()
    transformed_df['icr'] = transformed_df['ebit']/ transformed_df['interest_expense'] 
    transformed_df['icr_ttm'] = transformed_df['ebit'].rolling(window=4).sum()/transformed_df['interest_expense'].rolling(window=4).sum()
    transformed_df.drop(columns=['interest_expense', 'ebit'], inplace=True)
    transformed_df = compute_growth_metrics(transformed_df, column="icr", score_regime=[-0.05, 0, 0.05, 0.2])
    transformed_df = compute_stability_metrics(transformed_df, column="icr", volatility_threshold=0.1)
    transformed_df = compute_accel_metrics(transformed_df, column="icr")
    return transformed_df


def load_records(transformed_df, conn):

    # Insert records into core.icr_metrics
    total_records = insert_records(conn, transformed_df, 'core.icr_metrics', ['tic', 'calendar_year', 'calendar_quarter'])
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
