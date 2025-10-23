import pandas as pd
from psycopg import connect
from typing import Dict

from sklearn import metrics

from server.database.utils import connect_to_db, insert_records, read_sql_query
from etl_pipeline.utils import calculate_pct_change, calculate_streak

def read_earnings(conn, tic: str) -> pd.DataFrame:
    """
    Fetch earnings data for a specific ticker from the core.earnings table.

    Args:
        conn: Database connection object.
        tic: Stock ticker symbol.

    Returns:
        pd.DataFrame: DataFrame containing earnings data for the given ticker.
    """

    query = f"""
        SELECT tic, calendar_year, calendar_quarter,
               eps, eps_estimated, revenue, revenue_estimated
        FROM core.earnings
        WHERE tic = '{tic}' 
            AND eps IS NOT NULL 
            AND revenue IS NOT NULL
        ORDER BY calendar_year, calendar_quarter;
    """
    df = read_sql_query(query, conn)
    df['eps'] = pd.to_numeric(df['eps'], errors='coerce')
    df['eps_estimated'] = pd.to_numeric(df['eps_estimated'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['revenue_estimated'] = pd.to_numeric(df['revenue_estimated'], errors='coerce')

    return df



def classify_eps_regime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify EPS regime based on the direction and sign transition of EPS.

    Args:
        df: DataFrame containing EPS and previous EPS data.

    Returns:
        pd.Series: Series containing EPS regime classifications.
    """
    
    df['eps_lag1'] = df['eps'].shift(1)
    column = "eps_regime"

    def eps_regime_logic(row: pd.Series) -> str:
        eps, eps_prev = row['eps'], row['eps_lag1']
        if pd.isnull(eps) or pd.isnull(eps_prev):
            return 'Unknown'
        if eps_prev < 0 < eps:
            return 'Turnaround'
        if eps_prev > 0 > eps:
            return 'Profit to Loss'
        if eps < 0 and eps_prev < 0 and eps > eps_prev:
            return 'Loss Narrowing'
        if eps < 0 and eps_prev < 0 and eps < eps_prev:
            return 'Loss Widening'
        if eps > 0 and eps_prev > 0 and eps > eps_prev:
            return 'Positive Growth'
        if eps > 0 and eps_prev > 0 and eps < eps_prev:
            return 'Profit Decline'
        if abs(eps - eps_prev) / max(abs(eps), abs(eps_prev), 1e-6) <= 0.05:
            return 'Flat'
        return 'Unknown'
    
    df[column] = df.apply(eps_regime_logic, axis=1)
    df.drop(columns=['eps_lag1'], inplace=True)
    return df



def compute_surprise_metrics(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    
    # Surprise Percentage
    df[f'{prefix}_surprise_pct'] = df.apply(lambda row: calculate_pct_change(row[f'{prefix}'], row[f'{prefix}_estimated']), axis=1)

    # Beat Count (Last 4 Quarters)
    df[f'{prefix}_beat_flag'] = (df[f'{prefix}_surprise_pct'] > 0).astype(int)
    df[f'{prefix}_beat_count_4q'] = df[f'{prefix}_beat_flag'].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
    
    # Beat Streak Length
    df[f'{prefix}_beat_streak_length'] = calculate_streak(df[f'{prefix}_beat_flag'])

    return df

def compute_surprise_classification(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """
    | **Range (surprise_pct)** | **Class** | **Meaning / Signal** |
    |:--|:--|:--|
    | ≥ **+10%** | **Major Beat** | Exceptional outperformance — significantly above expectations. |
    | **+3% to +10%** | **Moderate Beat** | Clear upside surprise — strong positive signal. |
    | **+1% to +3%** | **Slight Beat** | Mild outperformance — modest but positive result. |
    | **−1% to +1%** | **In-Line** | Effectively met expectations — neutral, within noise tolerance. |
    | **−5% to −1%** | **Slight Miss** | Small shortfall — mild underperformance. |
    | ≤ **−5%** | **Major Miss** | Clear disappointment — significant underperformance. |
    """

    class_column = f'{prefix}_surprise_class'
    surprise_column = f'{prefix}_surprise_pct'

    def classification_logic(surprise: float) -> str:
        if pd.isnull(surprise):
            return 'Unknown'
        if surprise >= 0.10:
            return 'Major Beat'
        elif 0.03 <= surprise < 0.10:
            return 'Moderate Beat'
        elif 0.01 <= surprise < 0.03:
            return 'Slight Beat'
        elif 0.0 <= surprise < 0.01:
            return 'In-Line (Positive)'
        elif -0.01 <= surprise < 0.0:
            return 'In-Line (Negative)'
        elif -0.05 <= surprise < -0.01:
            return 'Slight Miss'
        elif surprise < -0.05:
            return 'Major Miss'
        else:
            return 'Unknown'
    df[class_column] = df[surprise_column].apply(classification_logic)

    return df

def compute_surprise_regime(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    count_column = f'{prefix}_beat_count_4q'
    streak_column = f'{prefix}_beat_streak_length'
    regime_column = f'{prefix}_surprise_regime'

    def regime_logic(row: pd.Series) -> str:
        if pd.isnull(row[count_column]) or pd.isnull(row[streak_column]):
            return 'Unknown'
        count = row[count_column]
        streak = row[streak_column]
        
        if count >= 3 and streak >= 3:
            return 'Consistent Outperformer'
        elif count >= 3 and 1 <= streak <= 2:
            return 'Frequent Beater'
        elif count == 3 and streak == 0:
            return 'Broken Streak'
        elif count == 2 and streak == 2:
            return 'Emerging Beater'
        elif count == 2 and streak < 2:
            return 'Mixed Performance'
        elif count <= 1 and streak <= 1:
            return 'Consistent Miss'
        else:
            return 'Unknown'
    df[regime_column] = df.apply(regime_logic, axis=1)
    return df
        
    



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
            df = classify_eps_regime(df)

            for prefix in ['eps', 'revenue']:
                df = compute_surprise_metrics(df, prefix)
                df = compute_surprise_classification(df, prefix)
                df = compute_surprise_regime(df, prefix)

 
            total_records = insert_records(conn, df, "core.earnings_analysis", ["tic", "calendar_year", "calendar_quarter"])
            print(f"Inserted/Updated {total_records} records into core.earnings_analysis for {tic}.")
        conn.close()
        # Display one record as a dictionary
        # record = df.iloc[-1].to_dict()
        # print(record)
    return


if __name__ == "__main__":
    main()


