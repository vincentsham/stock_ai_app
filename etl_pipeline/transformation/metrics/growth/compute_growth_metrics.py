from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf
import numpy as np
from etl_pipeline.utils import convert_decimals_to_float


def transform_records(conn, tic: str, date: str) -> pd.DataFrame:
    close_price_query = f"""
        SELECT tic, date::date, close AS close_price
        FROM raw.stock_ohlcv_daily
        WHERE tic = '{tic}' AND date::date >= '{date}'::date
        ORDER BY date;
    """
    df = read_sql_query(close_price_query, conn)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df = convert_decimals_to_float(df)

    balance_sheet_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, 
            total_assets
        FROM core.balance_sheets_quarterly
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """

    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')
    df_balance_sheet = convert_decimals_to_float(df_balance_sheet)

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, eps_diluted AS eps_gaap, revenue AS revenue_gaap,
               ebitda, operating_income, weighted_average_shares_diluted AS shares_outstanding
        FROM core.income_statements_quarterly 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')
    df_income = convert_decimals_to_float(df_income)

    df_income['ebitda_ttm'] = df_income['ebitda'].rolling(window=4).sum()
    df_income['ebitda_ttm_prev'] = df_income['ebitda_ttm'].shift(4)
    df_income['ebitda_ttm_3y_ago'] = df_income['ebitda_ttm'].shift(12)
    df_income['ebitda_ttm_5y_ago'] = df_income['ebitda_ttm'].shift(20)

    df_income['operating_income_ttm'] = df_income['operating_income'].rolling(window=4).sum()
    df_income['operating_income_ttm_prev'] = df_income['operating_income_ttm'].shift(4)

    df_income['eps_gaap_ttm'] = df_income['eps_gaap'].rolling(window=4).sum()
    df_income['eps_gaap_ttm_prev'] = df_income['eps_gaap_ttm'].shift(4)
    df_income['eps_gaap_ttm_3y_ago'] = df_income['eps_gaap_ttm'].shift(12)
    df_income['eps_gaap_ttm_5y_ago'] = df_income['eps_gaap_ttm'].shift(20)

    df_income['revenue_gaap_ttm'] = df_income['revenue_gaap'].rolling(window=4).sum()
    df_income['revenue_gaap_ttm_prev'] = df_income['revenue_gaap_ttm'].shift(4)
    df_income['revenue_gaap_ttm_3y_ago'] = df_income['revenue_gaap_ttm'].shift(12)
    df_income['revenue_gaap_ttm_5y_ago'] = df_income['revenue_gaap_ttm'].shift(20)

    
    cash_flow_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, free_cash_flow as fcf
        FROM core.cash_flow_statements_quarterly
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_cash_flow = read_sql_query(cash_flow_statement_query, conn)
    df_cash_flow['earnings_date'] = pd.to_datetime(df_cash_flow['earnings_date'])
    df_cash_flow = df_cash_flow.sort_values('earnings_date')
    df_cash_flow = convert_decimals_to_float(df_cash_flow)

    df_cash_flow['fcf_ttm'] = df_cash_flow['fcf'].rolling(window=4).sum()
    df_cash_flow['fcf_ttm_prev'] = df_cash_flow['fcf_ttm'].shift(4)
    df_cash_flow['fcf_ttm_3y_ago'] = df_cash_flow['fcf_ttm'].shift(12)
    df_cash_flow['fcf_ttm_5y_ago'] = df_cash_flow['fcf_ttm'].shift(20)

    earnings_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, 
               eps, eps_estimated, revenue, revenue_estimated
        FROM core.earnings
        WHERE tic = '{tic}' AND eps_estimated IS NOT NULL
        ORDER BY earnings_date;
    """
    df_earnings = read_sql_query(earnings_query, conn)
    df_earnings['earnings_date'] = pd.to_datetime(df_earnings['earnings_date'])
    df_earnings = df_earnings.sort_values('earnings_date')
    df_earnings = convert_decimals_to_float(df_earnings)

    df_earnings['eps_est_ttm'] = df_earnings['eps_estimated'].rolling(window=4).sum()
    df_earnings['eps_forward'] = df_earnings['eps_est_ttm'].shift(-4)
    df_earnings['eps_ttm'] = df_earnings['eps'].rolling(window=4).sum()
    df_earnings['eps_ttm_prev'] = df_earnings['eps_ttm'].shift(4)
    df_earnings['eps_ttm_3y_ago'] = df_earnings['eps_ttm'].shift(12)
    df_earnings['eps_ttm_5y_ago'] = df_earnings['eps_ttm'].shift(20)
    df_earnings['eps_forward_growth_rate'] = df_earnings.apply(
        lambda r: (r['eps_forward'] - r['eps_ttm']) / abs(r['eps_ttm'])
        if pd.notna(r['eps_forward']) and pd.notna(r['eps_ttm']) and r['eps_ttm'] != 0
        else np.nan,
        axis=1
    )
    df_earnings['eps_forward_growth_rate'] = df_earnings['eps_forward_growth_rate'].ffill()
    df_earnings.loc[df_earnings['eps_forward'].isna(), 'eps_forward'] = df_earnings.loc[df_earnings['eps_forward'].isna()].apply(
        lambda r: float(r['eps_ttm']) * (1 + r['eps_forward_growth_rate'])
        if pd.notna(r['eps_forward_growth_rate']) and pd.notna(r['eps_ttm']) else np.nan, axis=1
    )


    df_earnings['revenue_est_ttm'] = df_earnings['revenue_estimated'].rolling(window=4).sum()
    df_earnings['revenue_forward'] = df_earnings['revenue_est_ttm'].shift(-4)
    df_earnings['revenue_ttm'] = df_earnings['revenue'].rolling(window=4).sum()
    df_earnings['revenue_ttm_prev'] = df_earnings['revenue_ttm'].shift(4)
    df_earnings['revenue_ttm_3y_ago'] = df_earnings['revenue_ttm'].shift(12)
    df_earnings['revenue_ttm_5y_ago'] = df_earnings['revenue_ttm'].shift(20)
    df_earnings['revenue_forward_growth_rate'] = df_earnings.apply(
        lambda r: (r['revenue_forward'] - r['revenue_ttm']) / abs(r['revenue_ttm'])
        if pd.notna(r['revenue_forward']) and pd.notna(r['revenue_ttm']) and r['revenue_ttm'] != 0
        else np.nan,
        axis=1
    )
    df_earnings['revenue_forward_growth_rate'] = df_earnings['revenue_forward_growth_rate'].ffill()
    df_earnings.loc[df_earnings['revenue_forward'].isna(), 'revenue_forward'] = df_earnings.loc[df_earnings['revenue_forward'].isna()].apply(
        lambda r: float(r['revenue_ttm']) * (1 + r['revenue_forward_growth_rate'])
        if pd.notna(r['revenue_forward_growth_rate']) and pd.notna(r['revenue_ttm']) else np.nan, axis=1
    )




    # eps_forward_growth_rate = df_earnings.loc[df_earnings.index[-5], 'eps_forward_growth_rate']
    # for i in [4, 3, 2]:
    #     _eps_forward = df_earnings.iloc[-i+1:]['eps_estimated'].sum()
    #     _eps_prev = df_earnings.iloc[-8+(5-i):-4]['eps'].sum()
    #     _eps_forward_growth_rate = (float(_eps_forward) - float(_eps_prev)) / abs(float(_eps_prev)) if _eps_prev > 0 else np.nan
    #     eps_forward_growth_rate = _eps_forward_growth_rate * (i - 1)/4 + eps_forward_growth_rate * (4 - (i - 1))/4 \
    #                                     if _eps_forward_growth_rate and eps_forward_growth_rate \
    #                                     else eps_forward_growth_rate or _eps_forward_growth_rate
    #     eps_forward = float(df_earnings['eps_ttm'].iloc[-i]) * (1 + eps_forward_growth_rate) \
    #                         if eps_forward_growth_rate else np.nan
    #     df_earnings.loc[df_earnings.index[-i], 'eps_forward'] = eps_forward
    #     df_earnings.loc[df_earnings.index[-i], 'eps_forward_growth_rate'] = eps_forward_growth_rate
    # df_earnings['eps_forward'] = df_earnings['eps_forward'].ffill()
    # df_earnings['eps_forward_growth_rate'] = df_earnings['eps_forward_growth_rate'].ffill()

    # ticker = yf.Ticker(tic)
    # pe_forward = ticker.info.get("forwardPE")
    # current_price = ticker.info.get("currentPrice")
    # eps_forward = current_price / pe_forward if pe_forward and pe_forward > 0 and current_price else np.nan
    # df_earnings.loc[df_earnings.index[-1], 'eps_forward'] = eps_forward
    # eps_forward_growth_rate = (eps_forward - float(df_earnings['eps_ttm'].iloc[-1])) / abs(float(df_earnings['eps_ttm'].iloc[-1])) \
    #                             if eps_forward and float(df_earnings['eps_ttm'].iloc[-1]) != 0 else np.nan
    # df_earnings.loc[df_earnings.index[-1], 'eps_forward_growth_rate'] = eps_forward_growth_rate
    
    # revenue_forward_growth_rate = df_earnings.loc[df_earnings.index[-5], 'revenue_forward_growth_rate']
    # for i in [4, 3, 2]:
    #     _revenue_forward = df_earnings.iloc[-i+1:]['revenue_estimated'].sum()
    #     _revenue_prev = df_earnings.iloc[-8+(5-i):-4]['revenue'].sum()
    #     _revenue_forward_growth_rate = (float(_revenue_forward) - float(_revenue_prev)) / abs(float(_revenue_prev)) if _revenue_prev > 0 else np.nan
    #     revenue_forward_growth_rate = _revenue_forward_growth_rate * (i - 1)/4 + revenue_forward_growth_rate * (4 - (i - 1))/4 \
    #                                     if _revenue_forward_growth_rate and revenue_forward_growth_rate \
    #                                     else revenue_forward_growth_rate or _revenue_forward_growth_rate
    #     revenue_forward = float(df_earnings['revenue_ttm'].iloc[-i]) * (1 + revenue_forward_growth_rate) \
    #                         if revenue_forward_growth_rate else np.nan
    #     df_earnings.loc[df_earnings.index[-i], 'revenue_forward'] = revenue_forward
    #     df_earnings.loc[df_earnings.index[-i], 'revenue_forward_growth_rate'] = revenue_forward_growth_rate
    # df_earnings['revenue_forward'] = df_earnings['revenue_forward'].ffill()
    # df_earnings['revenue_forward_growth_rate'] = df_earnings['revenue_forward_growth_rate'].ffill() 

    df = pd.merge_asof(
            df, df_balance_sheet,
            left_on="date",
            right_on="earnings_date",
            by="tic",
            direction="backward",
            allow_exact_matches=True
        )
    df = df.drop(columns=['earnings_date', 'calendar_year', 'calendar_quarter'])
    df = pd.merge_asof(
            df, df_income,
            left_on="date",
            right_on="earnings_date",
            by="tic",
            direction="backward",
            allow_exact_matches=True
        )
    df = df.drop(columns=['earnings_date', 'calendar_year', 'calendar_quarter'])
    df = pd.merge_asof(
            df, df_cash_flow,
            left_on="date",
            right_on="earnings_date",
            by="tic",
            direction="backward",
            allow_exact_matches=True
        )
    df = df.drop(columns=['earnings_date', 'calendar_year', 'calendar_quarter'])
    df = pd.merge_asof(
            df, df_earnings,
            left_on="date",
            right_on="earnings_date",
            by="tic",
            direction="backward",
            allow_exact_matches=True
        )
    df = df.drop(columns=['earnings_date', 'calendar_year', 'calendar_quarter'])
    
    df['market_cap'] = df['close_price'] * df['shares_outstanding']

    df['revenue_growth_yoy'] = df.apply(
        lambda row: (float(row['revenue_ttm']) - float(row['revenue_ttm_prev'])) / abs(float(row['revenue_ttm_prev']))
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_prev']) and row['revenue_ttm_prev'] != 0 else np.nan, axis=1
    )
    df['revenue_cagr_3y'] = df.apply(
        lambda row: (float(row['revenue_ttm']) / float(row['revenue_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_3y_ago']) and row['revenue_ttm_3y_ago'] > 0 else np.nan, axis=1
    )
    df['revenue_cagr_5y'] = df.apply(
        lambda row: (float(row['revenue_ttm']) / float(row['revenue_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_5y_ago']) and row['revenue_ttm_5y_ago'] > 0 else np.nan, axis=1
    )

    df['eps_growth_yoy'] = df.apply(
        lambda row: (float(row['eps_ttm']) - float(row['eps_ttm_prev'])) / abs(float(row['eps_ttm_prev']))
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_prev']) and row['eps_ttm_prev'] != 0 else np.nan, axis=1
    )
    df['eps_cagr_3y'] = df.apply(
        lambda row: (float(row['eps_ttm']) / float(row['eps_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_3y_ago']) and row['eps_ttm_3y_ago'] > 0 else np.nan, axis=1
    )
    df['eps_cagr_5y'] = df.apply(
        lambda row: (float(row['eps_ttm']) / float(row['eps_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_5y_ago']) and row['eps_ttm_5y_ago'] > 0 else np.nan, axis=1
    )

    df['fcf_growth_yoy'] = df.apply(
        lambda row: (float(row['fcf_ttm']) - float(row['fcf_ttm_prev'])) / abs(float(row['fcf_ttm_prev']))
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_prev']) and row['fcf_ttm_prev'] != 0 else np.nan, axis=1
    )
    df['fcf_cagr_3y'] = df.apply(
        lambda row: (float(row['fcf_ttm']) / float(row['fcf_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_3y_ago']) and row['fcf_ttm_3y_ago'] > 0 else np.nan, axis=1
    )
    df['fcf_cagr_5y'] = df.apply(
        lambda row: (float(row['fcf_ttm']) / float(row['fcf_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_5y_ago']) and row['fcf_ttm_5y_ago'] > 0 else np.nan, axis=1
    )

    df['ebitda_growth_yoy'] = df.apply(
        lambda row: (float(row['ebitda_ttm']) - float(row['ebitda_ttm_prev'])) / abs(float(row['ebitda_ttm_prev']))
        if pd.notna(row['ebitda_ttm']) and pd.notna(row['ebitda_ttm_prev']) and row['ebitda_ttm_prev'] != 0 else np.nan, axis=1
    )
    df['ebitda_cagr_3y'] = df.apply(
        lambda row: (float(row['ebitda_ttm']) / float(row['ebitda_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['ebitda_ttm']) and pd.notna(row['ebitda_ttm_3y_ago']) and row['ebitda_ttm_3y_ago'] > 0 else np.nan, axis=1
    )
    df['ebitda_cagr_5y'] = df.apply(
        lambda row: (float(row['ebitda_ttm']) / float(row['ebitda_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['ebitda_ttm']) and pd.notna(row['ebitda_ttm_5y_ago']) and row['ebitda_ttm_5y_ago'] > 0 else np.nan, axis=1
    )
    df['operating_income_growth_yoy'] = df.apply(
        lambda row: (float(row['operating_income_ttm']) - float(row['operating_income_ttm_prev'])) / abs(float(row['operating_income_ttm_prev']))
        if pd.notna(row['operating_income_ttm']) and pd.notna(row['operating_income_ttm_prev']) and row['operating_income_ttm_prev'] != 0 else np.nan, axis=1
    )
    df['forward_eps_growth'] = df['eps_forward_growth_rate']
    df['forward_revenue_growth'] = df['revenue_forward_growth_rate']

 
    transformed_df = df[[
        'tic', 'date', 
        'revenue_growth_yoy', 'revenue_cagr_3y',
        'eps_growth_yoy', 'eps_cagr_3y',
        'fcf_growth_yoy', 'fcf_cagr_3y',
        'revenue_cagr_5y', 'eps_cagr_5y', 'fcf_cagr_5y',
        'ebitda_growth_yoy', 'ebitda_cagr_3y',
        'ebitda_cagr_5y',
        'operating_income_growth_yoy',
        'forward_eps_growth', 'forward_revenue_growth'
    ]]

    # Ensure DB inserts get Python np.nan instead of NaN.
    transformed_df = transformed_df.where(pd.notna(transformed_df), np.nan)

    return transformed_df




def load_records(transformed_df, conn):

    # Insert records into core.growth_metrics
    total_records = insert_records(conn, transformed_df, 'core.growth_metrics', ['tic', 'date'])
    return total_records

def main():
    # Connect to the database
    conn = connect_to_db()
    if conn is not None:
        # Extract records
        cursor = conn.cursor()
        query = """
            SELECT tic
            FROM core.stock_profiles;
        """
        cursor.execute(query)
        tics = cursor.fetchall()
        for tic in tics:
            tic = tic[0]
            subquery = f"""
                    SELECT tic, earnings_date::date
                    FROM core.balance_sheets_quarterly
                    WHERE tic = '{tic}'
                    ORDER BY earnings_date
                    LIMIT 1;
            """
            cursor.execute(subquery)
            record = cursor.fetchall()[0]
            print(f"Processing tic: {tic} for date starting from {record[0]} - {record[1]}")
            transformed_df = transform_records(conn, record[0], record[1])
            if transformed_df.empty:
                print("No new or updated records to process.")
                continue
  
            total_records = load_records(transformed_df, conn)
            print(f"Total records inserted/updated for {tic}: {total_records}")

    return


if __name__ == "__main__":
    main()
