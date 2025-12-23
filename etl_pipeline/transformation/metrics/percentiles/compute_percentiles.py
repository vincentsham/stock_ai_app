from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf
import numpy as np



def transform_records(df: pd.DataFrame) -> pd.DataFrame:
    
    transformed_df = df[['inference_id', 'tic', 'date']].copy()
    columns = df.columns.tolist()
    metric_columns = [col for col in columns if col not in ['inference_id', 'tic', 'date', 'updated_at']]

    # Calculate percentiles for each metric column
    for col in metric_columns:
        percentile_col = f"{col}_percentile"
        transformed_df[percentile_col] = df[col].rank(pct=True) * 100
        # None or NaN values => np.nan
        transformed_df.loc[df[col].isnull(), percentile_col] = np.nan
    return transformed_df


def load_records(transformed_df, table, conn):
    # Insert records into core.valuation_percentiles
    total_records = insert_records(conn, transformed_df, table, ['inference_id'])
    return total_records



def main():
    # Connect to the database
    tables = [['core.valuation_metrics', 'core.valuation_percentiles'],
              ['core.profitability_metrics', 'core.profitability_percentiles'],
              ['core.growth_metrics', 'core.growth_percentiles'],
              ['core.efficiency_metrics', 'core.efficiency_percentiles'],
              ['core.financial_health_metrics', 'core.financial_health_percentiles'],          
            ]
    conn = connect_to_db()
    if conn is not None:
        # Extract records
        cursor = conn.cursor()
        for table_pair in tables:
            source_table = table_pair[0]
            target_table = table_pair[1]
            query = f"""
                SELECT *
                FROM {source_table};
            """
            df = read_sql_query(query, conn)
            transformed_df = transform_records(df)
            total_records = load_records(transformed_df, target_table, conn)
            print(f"Total records inserted/updated into {target_table}: {total_records}")

    return


if __name__ == "__main__":
    main()
