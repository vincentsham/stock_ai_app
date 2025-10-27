from server.database.utils import connect_to_db, insert_records, read_sql_query
from etl_pipeline.utils import timestamp_to_trading_date, convert_numpy_types
import pandas as pd
import numpy as np


def read_ohlcv_data(tic, conn):
    query = f"""
        SELECT tic, date, open, high, low, close, volume
        FROM raw.stock_ohlcv_daily
        WHERE tic = '{tic}';
    """
    df = read_sql_query(query, conn)
    return df


def read_analyst_pts(tic, conn):
    query = f"""
        SELECT tic, published_at::timestamp AT TIME ZONE 'America/New_York' AS published_at,
                title, site, analyst_name, company, 
                price_target, adj_price_target, price_when_posted
        FROM core.analyst_price_targets
        WHERE tic = '{tic}'
        ORDER BY published_at;
    """
    df = read_sql_query(query, conn)
    return df


def find_previous_pts(df):
    """
    Annotate a PT DataFrame with previous-note context per (tic, analyst).

    This function:
      1) Chooses the effective price target `pt` (prefers `adj_price_target` over `price_target`).
      2) Sorts rows deterministically by ['tic','analyst_name','published_at'].
      3) Adds previous-note fields per (tic, analyst_name):
         - prev_pt, prev_price_when_posted, prev_published_at, prev_url
      4) Computes `pt_delta = pt - prev_pt`.
      5) Classifies the absolute PT direction:
         - 'initialize' if no prev_pt
         - 'upgrade' if pt > prev_pt
         - 'downgrade' if pt < prev_pt
         - 'reiterate' otherwise
      6) Resort by ['tic','published_at'] for downstream windowing.

    Args:
        df (pd.DataFrame): Must contain columns:
            ['tic','published_at','analyst_name','price_target','adj_price_target',
             'price_when_posted','url'] (url optional for prev_url; if missing,
             resulting column will be NaN).

    Returns:
        pd.DataFrame: Original columns plus:
            - pt (float)
            - prev_pt (float), prev_price_when_posted (float), prev_published_at (timestamp), prev_url (str)
            - pt_delta (float)
            - pt_change (str in {'initialize','upgrade','downgrade','reiterate'})

    Notes:
        - Grouping columns are ['tic','analyst_name'] to scope “previous” by analyst.
          Add 'company' to the group if needed for more granular scoping.
        - Does not apply any date filtering; do this upstream/downstream.
    """
    df = df.copy()  # Ensure we are working on a copy
    # Choose adjusted PT when available
    df.loc[:, 'pt'] = df['adj_price_target'].fillna(df['price_target'])
    # Sort so shift() is deterministic (tie-break with url)

    df = df.sort_values(['tic', 'analyst_name', 'published_at'])

    # Previous PT within (tic, analyst); include 'company' too if you want stricter scoping
    grp_cols = ['tic', 'analyst_name']
    df.loc[:, 'prev_pt'] = df.groupby(grp_cols, sort=False)['pt'].shift(1)
    df.loc[:, 'prev_price_when_posted'] = df.groupby(grp_cols, sort=False)['price_when_posted'].shift(1)
    df.loc[:, 'prev_published_at'] = df.groupby(grp_cols, sort=False)['published_at'].shift(1)
    # df['prev_url'] = df.groupby(grp_cols, sort=False)['url'].shift(1)

    df.loc[:, 'pt_delta'] = df['pt'] - df['prev_pt']
    df.loc[:, 'pt_change'] = np.select(
        [
            df['prev_pt'].isna(),
            df['pt'] > df['prev_pt'],
            df['pt'] < df['prev_pt'],
        ],
        ['initialize', 'upgrade', 'downgrade'],
        default='reiterate'
    )
    df = df.sort_values(['tic', 'published_at'])
    return df


def read_analyst_grades(tic, conn):
    query = f"""
        SELECT tic, published_at::timestamp AT TIME ZONE 'America/New_York' AS published_at, 
                title, site, company, 
                new_grade, previous_grade, action, price_when_posted
        FROM core.analyst_grades
        WHERE tic = '{tic}';
    """
    df = read_sql_query(query, conn)

    return df


def aggregate_analyst_pts(df, start_date, end_date):
    """
    Aggregate price target (PT) statistics and PT action counts for a 30-day window.

    Applies trading-date attribution via `timestamp_to_trading_date`, filters rows
    to (start_date, end_date] (open-right interval), and computes:
      - pt_stats: {count, high, low, p25, median, p75, mean, stddev, dispersion}
      - pt_actions: {upgrade_n, downgrade_n, reiterate_n, init_n}
        (based on `pt_change` from `find_previous_pts`)

    Args:
        df (pd.DataFrame): Analyst PT notes with at least:
            ['tic','published_at','pt','pt_change'] and optionally
            ['price_target','adj_price_target'] if `pt` isn’t precomputed.
        start_date (date): Exclusive lower bound of the window.
        end_date (date): Inclusive upper bound of the window.

    Returns:
        dict: {
          "pt_stats": {...},
          "pt_actions": {...}
        }

    Notes:
        - `dispersion` = p75 - p25; fallback to (high - low) if quantiles unavailable.
        - Ensure `find_previous_pts` has been applied before calling this function
          if you want accurate action counts.
    """
    df = df.copy()  # Ensure we are working on a copy
    df.loc[:, 'trading_date'] = df['published_at'].apply(timestamp_to_trading_date)
    df = df[(df['trading_date'] <= end_date) & (df['trading_date'] > start_date)]

    df.loc[:, 'pt'] = df['pt'].astype(float)
    pt_stats = {
        "pt_count": len(df),
        "pt_high": df['pt'].max(),
        "pt_low": df['pt'].min(),
        "pt_p25": df['pt'].quantile(0.25),
        "pt_median": df['pt'].median(),
        "pt_p75": df['pt'].quantile(0.75),
        "pt_mean": df['pt'].mean(),
        "pt_stddev": df['pt'].std(),
        "pt_dispersion": df['pt'].quantile(0.75) - df['pt'].quantile(0.25) if not df['pt'].empty else df['pt'].max() - df['pt'].min()
    }

    pt_actions = {
        "pt_upgrade_n": (df['pt_change'] == 'upgrade').sum(),
        "pt_downgrade_n": (df['pt_change'] == 'downgrade').sum(),
        "pt_reiterate_n": (df['pt_change'] == 'reiterate').sum(),
        "pt_init_n": (df['pt_change'] == 'initialize').sum()
    }

    return {"pt_stats": pt_stats, "pt_actions": pt_actions}


def aggregate_analyst_grades(df, start_date, end_date):
    """
    Aggregate grade distribution and grade action counts for a 30-day window.

    Applies trading-date attribution via `timestamp_to_trading_date`, filters rows
    to (start_date, end_date], and computes:
      - grade_stats: {count, buy_n, hold_n, sell_n, buy_ratio, hold_ratio,
                      sell_ratio, grade_balance}
      - grade_actions: {upgrade_n, downgrade_n, reiterate_n, init_n}

    Args:
        df (pd.DataFrame): Analyst grade actions with at least:
            ['tic','published_at','new_grade','previous_grade','grade_change'].
            Grades should be (or be mappable to) Buy/Hold/Sell.
        start_date (date): Exclusive lower bound.
        end_date (date): Inclusive upper bound.

    Returns:
        dict: {
          "grade_stats": {...},
          "grade_actions": {...}
        }

    Notes:
        - `grade_balance` = (buy_n - sell_n) / count.
        - Apply your grade normalization map before calling this function.
    """
    df = df.copy()  # Ensure we are working on a copy
    df.loc[:, 'trading_date'] = df['published_at'].apply(timestamp_to_trading_date)
    df = df[(df['trading_date'] <= end_date) & (df['trading_date'] > start_date)]

    grade_stats = {
        "grade_count": len(df),
        "grade_buy_n": (df['new_grade'] == 1).sum(),
        "grade_hold_n": (df['new_grade'] == 0).sum(),
        "grade_sell_n": (df['new_grade'] == -1).sum(),
        "grade_buy_ratio": (df['new_grade'] == 1).sum() / len(df) if len(df) > 0 else 0,
        "grade_hold_ratio": (df['new_grade'] == 0).sum() / len(df) if len(df) > 0 else 0,
        "grade_sell_ratio": (df['new_grade'] == -1).sum() / len(df) if len(df) > 0 else 0,
        "grade_balance": (df['new_grade'].sum() / len(df) if len(df) > 0 else 0)
    }

    grade_actions = {
        "grade_upgrade_n": (df['action'] == 'upgrade').sum(),
        "grade_downgrade_n": (df['action'] == 'downgrade').sum(),
        "grade_reiterate_n": (df['action'] == 'reiterate').sum(),
        "grade_init_n": (df['action'] == 'initialize').sum()
    }

    return {"grade_stats": grade_stats, "grade_actions": grade_actions}


def aggregate_analyst_returns(df, start_date, end_date):
    """
    Aggregate analyst-implied return statistics and return action counts.

    Implied return per note is defined as:
        return_i = (pt_i / price_when_posted_i) - 1
    This function:
      1) Attributes events to trading dates via `timestamp_to_trading_date`.
      2) Filters to (start_date, end_date].
      3) Computes return_stats: {mean, median, p25, p75, stddev, dispersion, high, low}.
      4) Computes return_actions: {upgrade_n, downgrade_n, reiterate_n, init_n} where
         changes are measured vs each analyst's previous note:
             Δreturn = return_new - return_prev
         and the upgrade/downgrade thresholds are **volatility-adjusted** using
         `price_stats.stddev` from the same window (see `stock_price_statistics`).

    Args:
        df (pd.DataFrame): Analyst PT notes with fields:
            ['tic','published_at','pt','price_when_posted','prev_pt','prev_price_when_posted']
            (previous fields required for Δreturn classification).
        start_date (date): Exclusive lower bound of the 30-day window.
        end_date (date): Inclusive upper bound of the 30-day window.

    Returns:
        dict: {
          "return_stats": {...},
          "return_actions": {...}
        }

    Notes:
        - Ensure previous-note fields are populated (e.g., via `find_previous_pts`)
          if you need return action counts.
        - The volatility-adjusted threshold should be sourced from
          `price_stats['stddev']` computed for the same (start_date, end_date].
    """
    df = df.copy()  # Ensure we are working on a copy
    df.loc[:, 'trading_date'] = df['published_at'].apply(timestamp_to_trading_date)
    df = df[(df['trading_date'] <= end_date) & (df['trading_date'] > start_date)]

    df.loc[:, 'implied_return'] = (df['pt'] / df['price_when_posted']) - 1
    df.loc[:, 'implied_return'] = df['implied_return'].astype(float)
    return_stats = {
        "ret_mean": df['implied_return'].mean(),
        "ret_median": df['implied_return'].median(),
        "ret_p25": df['implied_return'].quantile(0.25),
        "ret_p75": df['implied_return'].quantile(0.75),
        "ret_stddev": df['implied_return'].std(),
        "ret_dispersion": df['implied_return'].quantile(0.75) - df['implied_return'].quantile(0.25) if not df['implied_return'].empty else df['implied_return'].max() - df['implied_return'].min(),
        "ret_high": df['implied_return'].max(),
        "ret_low": df['implied_return'].min()
    }

    # Compute return changes vs previous note per analyst
    df.loc[:, 'price_when_posted'] = df['price_when_posted'].astype(float)
    df.loc[:, 'return_delta'] = df['implied_return'] - df['implied_return'].shift(1)
    return_actions = {
        "ret_upgrade_n": (df['return_delta'] > df['price_when_posted'].std()).sum(),
        "ret_downgrade_n": (df['return_delta'] < -df['price_when_posted'].std()).sum(),
        "ret_reiterate_n": ((df['return_delta'] <= df['price_when_posted'].std()) & (df['return_delta'] >= -df['price_when_posted'].std())).sum(),
        "ret_init_n": df['return_delta'].isna().sum()
    }

    return {"ret_stats": return_stats, "ret_actions": return_actions}


def stock_price_statistics(df, start_date, end_date):
    """
    Compute price statistics over the 30-day window for volatility-aware comparisons.

    Filters daily OHLCV rows to (start_date, end_date] and computes summary stats
    on the `close` (or `adj close` if your input has it). Intended to produce the
    `price_stats` block used both for context and as a **dynamic threshold source**
    (stddev) for volatility-adjusted return action classification.

    Args:
        df (pd.DataFrame): Daily price data with columns:
            ['tic','date','open','high','low','close','volume'].
        start_date (date): Exclusive lower bound of the window.
        end_date (date): Inclusive upper bound of the window.

    Returns:
        dict: {
          "price_stats": {
            "start": float,
            "end": float,
            "high": float,
            "low": float,
            "p25": float,
            "median": float,
            "p75": float,
            "mean": float,
            "stddev": float
          }
        }

    Notes:
        - Uses the first and last available closes within the window for `start`/`end`.
        - If your pipeline uses adjusted prices, pass that column as `close`.
        - The returned `stddev` (of daily closes) is referenced by `aggregate_analyst_returns`
          to set volatility-adjusted thresholds for return upgrades/downgrades.
    """
    df = df.copy()  # Ensure we are working on a copy
    df = df[(df['date'] <= end_date) & (df['date'] > start_date)]

    df.loc[:, 'close'] = df['close'].astype(float)
    price_stats = {
        "price_start": df['close'].iloc[0] if not df.empty else None,
        "price_end": df['close'].iloc[-1] if not df.empty else None,
        "price_high": df['close'].max(),
        "price_low": df['close'].min(),
        "price_p25": df['close'].quantile(0.25),
        "price_median": df['close'].median(),
        "price_p75": df['close'].quantile(0.75),
        "price_mean": df['close'].mean(),
        "price_stddev": df['close'].std()
    }

    return {"price_stats": price_stats}


def transform_records(tic, conn, cursor, num_months, latest_date):
    results = []

    # Fetch data
    ohlcv_data = read_ohlcv_data(tic, conn)
    analyst_pts = read_analyst_pts(tic, conn)
    analyst_grades = read_analyst_grades(tic, conn)

    # Process data
    analyst_pts = find_previous_pts(analyst_pts)

    cursor.execute(f"SELECT date FROM raw.stock_ohlcv_daily WHERE tic = '{tic}';")
    dates = cursor.fetchall()

    for date in dates:
        end_date = date[0]
        start_date = (date[0] - pd.DateOffset(months=num_months)).date()

        if start_date < latest_date:
            continue  # Skip if start_date is before the latest_date threshold

        pt_aggregations = {}
        return_aggregations = {}
        if not analyst_pts.empty:
            pt_aggregations = aggregate_analyst_pts(analyst_pts, start_date, end_date)
            return_aggregations = aggregate_analyst_returns(analyst_pts, start_date, end_date)
        
        grade_aggregations = {}
        if not analyst_grades.empty:
            grade_aggregations = aggregate_analyst_grades(analyst_grades, start_date, end_date)
        price_aggregations = stock_price_statistics(ohlcv_data, start_date, end_date)

        # Combine results
        if analyst_pts.empty and analyst_grades.empty:
            continue  # Skip if no data to aggregate

        result = {
            "tic": tic,
            "start_date": start_date,
            "end_date": end_date,
            **pt_aggregations['pt_stats'],
            **pt_aggregations['pt_actions'],
            **grade_aggregations['grade_stats'],
            **grade_aggregations['grade_actions'],
            **return_aggregations['ret_stats'],
            **return_aggregations['ret_actions'],
            **price_aggregations['price_stats'],
        }

        results.append(result)
    
    df = pd.DataFrame(results)
    return df

def main():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        tic_list = cursor.fetchall()

        # Control how far back to process data
        latest_date = (pd.Timestamp.today() - pd.Timedelta(days=365 * 2)).date()


        for tic in tic_list:
            tic = tic[0]
            df = transform_records(tic, conn, cursor, 1, latest_date)
            total_records = insert_records(conn, df, "core.analyst_rating_monthly_summary", ["tic", "end_date"])
            print(f"Processed {total_records} monthly records for {tic}")

            df = transform_records(tic, conn, cursor, 3, latest_date)
            total_records = insert_records(conn, df, "core.analyst_rating_quarterly_summary", ["tic", "end_date"])
            print(f"Processed {total_records} quarterly records for {tic}")

            df = transform_records(tic, conn, cursor, 12, latest_date)
            total_records = insert_records(conn, df, "core.analyst_rating_yearly_summary", ["tic", "end_date"])
            print(f"Processed {total_records} yearly records for {tic}")

        conn.close()

if __name__ == "__main__":
    main()