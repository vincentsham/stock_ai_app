from server.database.utils import connect_to_db, execute_query, insert_records, read_sql_query
from etl_pipeline.transformation.financials.gsa_framework.compute_growth_metrics import compute_growth_metrics 
from etl_pipeline.transformation.financials.gsa_framework.compute_stability_metrics import compute_stability_metrics
from etl_pipeline.transformation.financials.gsa_framework.compute_accel_metrics import compute_accel_metrics 
import pandas as pd

def read_records(conn, tic: str) -> pd.DataFrame:
    query = f"""
        SELECT i.event_id, i.tic, i.calendar_year, i.calendar_quarter, i.net_income, i.revenue, i.raw_json_sha256
        FROM core.income_statements as i
        LEFT JOIN core.profit_margin_metrics as r 
        ON i.tic = r.tic
            AND i.calendar_year = r.calendar_year
            AND i.calendar_quarter = r.calendar_quarter
        WHERE i.tic = '{tic}'
            AND (r.raw_json_sha256 IS NULL OR r.raw_json_sha256 <> i.raw_json_sha256)
        ORDER BY i.tic, i.calendar_year, i.calendar_quarter;
    """
    df = read_sql_query(query, conn)
    print(f"Records to process: {len(df)}")
    return df


def transform_records(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = df.copy()
    transformed_df['profit_margin'] = transformed_df['net_income'] / transformed_df['revenue']
    transformed_df['profit_margin_ttm'] = transformed_df['net_income'].rolling(window=4).sum()/ transformed_df['revenue'].rolling(window=4).sum()
    transformed_df.drop(columns=['net_income', 'revenue'], inplace=True)
    transformed_df = compute_growth_metrics(transformed_df, column="profit_margin", score_regime=[-0.1, 0, 0.1, 0.3])
    transformed_df = compute_stability_metrics(transformed_df, column="profit_margin", volatility_threshold=0.03)
    transformed_df = compute_accel_metrics(transformed_df, column="profit_margin")
    return transformed_df


def load_records(transformed_df, conn):

    # Insert records into core.profit_margin_metrics
    total_records = insert_records(conn, transformed_df, 'core.profit_margin_metrics', ['tic', 'calendar_year', 'calendar_quarter'])
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
