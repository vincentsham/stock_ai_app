import pandas as pd
from psycopg import connect
from typing import Dict

from sklearn import metrics

from server.database.utils import connect_to_db
from etl_pipeline.utils import read_sql_query

def read_earnings(conn, tic: str) -> pd.DataFrame:
    """
    Fetch earnings data for a specific ticker from the raw.earnings table.

    Args:
        conn: Database connection object.
        tic: Stock ticker symbol.

    Returns:
        pd.DataFrame: DataFrame containing earnings data for the given ticker.
    """

    query = f"""
        SELECT tic, fiscal_year, fiscal_quarter,
               eps, eps_estimated, revenue, revenue_estimated
        FROM raw.earnings
        WHERE tic = '{tic}' 
            AND eps IS NOT NULL 
            AND revenue IS NOT NULL
        ORDER BY fiscal_year, fiscal_quarter;
    """
    df = read_sql_query(query, conn)
    df['eps'] = pd.to_numeric(df['eps'], errors='coerce')
    df['eps_estimated'] = pd.to_numeric(df['eps_estimated'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['revenue_estimated'] = pd.to_numeric(df['revenue_estimated'], errors='coerce')

    return df


def calculate_pct_change(current: float, previous: float) -> float:
    if previous is None or previous == 0 or current is None:
        return None
    
    pct_change = (current - previous) / max(abs(previous), 1e-6)

    # Cap the percentage changewithin ±1000%
    return max(min(pct_change, 10.0), -10.0)


def classify_eps_phase(row: pd.Series) -> str:
    """
    Classify EPS phase based on the direction and sign transition of EPS.

    Args:
        df: DataFrame containing EPS and previous EPS data.

    Returns:
        pd.Series: Series containing EPS phase classifications.
    """

    eps, eps_prev = row['eps'], row['eps_lag1']
    if pd.isnull(eps) or pd.isnull(eps_prev):
        return 'unknown'
    if eps_prev < 0 < eps:
        return 'turnaround'
    if eps_prev > 0 > eps:
        return 'profit_to_loss'
    if eps < 0 and eps_prev < 0 and eps > eps_prev:
        return 'loss_narrowing'
    if eps < 0 and eps_prev < 0 and eps < eps_prev:
        return 'loss_widening'
    if eps > 0 and eps_prev > 0 and eps > eps_prev:
        return 'positive_growth'
    if eps > 0 and eps_prev > 0 and eps < eps_prev:
        return 'profit_decline'
    if abs(eps - eps_prev) / max(abs(eps), abs(eps_prev), 1e-6) <= 0.05:
        return 'flat_or_neutral'
    return 'unknown'

def calculate_streak(series: pd.Series, on_value=1) -> pd.Series:
    """
    Vectorized run-length of consecutive `on_value` up to each row.
    Example: [1,1,0,1,1,1] -> [1,2,0,1,2,3]
    NaN is treated as not-on.
    """
    s = series.eq(on_value).fillna(False).astype(int)
    # group by breaks where s == 0, then cumulative count within each group
    out = s.groupby((s == 0).cumsum()).cumsum()
    # ensure zeros where the flag is off
    out = out.where(s.astype(bool), 0)
    return out

def compute_surprise_metrics(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    
    # Surprise Percentage
    df[f'{prefix}_surprise_pct'] = df.apply(lambda row: calculate_pct_change(row[f'{prefix}'], row[f'{prefix}_estimated']), axis=1)

    # Beat Count (Last 4 Quarters)
    df[f'{prefix}_beat_flag'] = (df[f'{prefix}_surprise_pct'] > 0).astype(int)
    df[f'{prefix}_beat_count_4q'] = df[f'{prefix}_beat_flag'].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
    
    # Beat Streak Length
    df[f'{prefix}_beat_streak_length'] = calculate_streak(df[f'{prefix}_beat_flag'])

    # Consistency (Volatility of Surprise)
    df[f'{prefix}_consistency'] = df[f'{prefix}_surprise_pct'].rolling(window=4).std()

    return df

def compute_growth_metrics(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    # Growth (QoQ)
    df[f'{prefix}_lag1'] = df[f'{prefix}'].shift(1)
    df[f'{prefix}_qoq_growth_pct'] = df.apply(lambda row: calculate_pct_change(row[f'{prefix}'], row[f'{prefix}_lag1']), axis=1)


    # Growth (YoY)
    df[f'{prefix}_lag4'] = df[f'{prefix}'].shift(4)
    df[f'{prefix}_yoy_growth_pct'] = df.apply(lambda row: calculate_pct_change(row[f'{prefix}'], row[f'{prefix}_lag4']), axis=1)

    # Growth Flag
    df[f'{prefix}_growth_flag'] = (df[f'{prefix}_yoy_growth_pct'] > 0).astype(int)
    df[f'{prefix}_growth_count_4q'] = df[f'{prefix}_growth_flag'].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
    # Growth Streak Length
    df[f'{prefix}_growth_streak_length'] = calculate_streak(df[f'{prefix}_growth_flag'])

    # Trend Strength
    df[f'{prefix}_trend_strength'] = df[f'{prefix}_yoy_growth_pct'].rolling(window=4).mean()

    # Consistency (Volatility of Growth)
    df[f'{prefix}_consistency'] = df[f'{prefix}_yoy_growth_pct'].rolling(window=4).std()

    # TTM Growth
    df[f'{prefix}_ttm_lag4'] = df[f'{prefix}_ttm'].shift(4)
    df[f'{prefix}_ttm_growth_pct'] = df.apply(lambda row: calculate_pct_change(row[f'{prefix}_ttm'], row[f'{prefix}_ttm_lag4']), axis=1)

    df = df.drop(columns=[f'{prefix}_lag1', f'{prefix}_lag4', f'{prefix}_ttm_lag4'])

    return df

def compute_acceleration_metrics(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    # Acceleration
    df[f'{prefix}_acceleration'] = df[f'{prefix}_yoy_growth_pct'].astype(float).diff().apply(lambda x: None if pd.isna(x) else x)

    # TTM Acceleration
    df[f'{prefix}_ttm_acceleration'] = df[f'{prefix}_ttm_growth_pct'].astype(float).diff().apply(lambda x: None if pd.isna(x) else x)

    # Acceleration Flag
    df[f'{prefix}_acceleration_flag'] = (df[f'{prefix}_acceleration'] > 0).astype(int)

    # Acceleration Count (Last 4 Quarters)
    df[f'{prefix}_acceleration_count_4q'] = df[f'{prefix}_acceleration_flag'].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)

    # Acceleration Streak Length
    df[f'{prefix}_acceleration_streak_length'] = calculate_streak(df[f'{prefix}_acceleration_flag'])

    return df



def insert_records(df: pd.DataFrame, conn):
    """
    Fast and minimal insert/upsert using psycopg cursor.execute with tuples.
    """
    # Replace NaN/NA with None for PostgreSQL compatibility
    df = df.replace({pd.NA: None, float('nan'): None})

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])

    sql = f"""
        INSERT INTO core.earnings_metrics ({', '.join(cols)})
        VALUES ({placeholders})
        ON CONFLICT (tic, fiscal_year, fiscal_quarter)
        DO UPDATE SET {updates}, updated_at = NOW();
    """

    try:
        with conn.cursor() as cursor:
            # Convert DataFrame to a sequence of tuples and execute in bulk
            data = tuple(df.itertuples(index=False, name=None))
            cursor.executemany(sql, data)  # ✅ psycopg safe bulk method
            total_records = cursor.rowcount
        conn.commit()
        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting earnings metrics: {e}")
        return 0

    

def main():
    
    # Connect to the database
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        tics = cursor.fetchall()
        for tic in tics:
            tic = tic[0]
            df = read_earnings(conn, tic)

            df['eps_lag1'] = df['eps'].shift(1)
            df['eps_phase'] = df.apply(classify_eps_phase, axis=1)
            for prefix in ['eps', 'revenue']:
                df[f'pre_{prefix}_flag'] = ((df[prefix] > 0).rolling(window=4).sum() == 0).astype(int)
                df[f'{prefix}_ttm'] = df[prefix].rolling(window=4).sum()
                df = compute_surprise_metrics(df, prefix)
                df = compute_growth_metrics(df, prefix)
                df = compute_acceleration_metrics(df, prefix)
            total_records = insert_records(df, conn)
            print(f"Inserted/Updated {total_records} records into core.earnings_metrics for {tic}.")
        conn.close()
        # Display one record as a dictionary
        # record = df.iloc[-1].to_dict()
        # print(record)
    return


if __name__ == "__main__":
    main()


