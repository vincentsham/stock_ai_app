from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf



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

    balance_sheet_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, total_assets,
            total_debt, total_stockholders_equity, cash_and_short_term_investments, cash_and_cash_equivalents
        FROM core.balance_sheets 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """

    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, 
               eps, revenue, ebitda, operating_income, 
               weighted_average_shs_out_dil AS shares_outstanding
        FROM core.income_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')

    df_income['eps_ttm'] = df_income['eps'].rolling(window=4).sum()
    df_income['eps_ttm_prev'] = df_income['eps_ttm'].shift(4)
    df_income['eps_ttm_3y_ago'] = df_income['eps_ttm'].shift(12)
    df_income['eps_ttm_5y_ago'] = df_income['eps_ttm'].shift(20)
    df_income['revenue_ttm'] = df_income['revenue'].rolling(window=4).sum()
    df_income['revenue_ttm_prev'] = df_income['revenue_ttm'].shift(4)
    df_income['revenue_ttm_3y_ago'] = df_income['revenue_ttm'].shift(12)
    df_income['revenue_ttm_5y_ago'] = df_income['revenue_ttm'].shift(20)
    df_income['ebitda_ttm'] = df_income['ebitda'].rolling(window=4).sum()
    df_income['ebitda_ttm_prev'] = df_income['ebitda_ttm'].shift(4)
    df_income['operating_income_ttm'] = df_income['operating_income'].rolling(window=4).sum()
    df_income['operating_income_ttm_prev'] = df_income['operating_income_ttm'].shift(4)

    
    cash_flow_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, free_cash_flow as fcf
        FROM core.cash_flow_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_cash_flow = read_sql_query(cash_flow_statement_query, conn)
    df_cash_flow['earnings_date'] = pd.to_datetime(df_cash_flow['earnings_date'])
    df_cash_flow = df_cash_flow.sort_values('earnings_date')
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
    df_earnings['eps_est_ttm'] = df_earnings['eps_estimated'].rolling(window=4).sum()
    df_earnings['eps_est_ttm_forward'] = df_earnings['eps_est_ttm'].shift(-4)
    df_earnings['eps_ttm'] = df_earnings['eps'].rolling(window=4).sum()

    df_earnings['revenue_est_ttm'] = df_earnings['revenue_estimated'].rolling(window=4).sum()
    df_earnings['revenue_est_ttm_forward'] = df_earnings['revenue_est_ttm'].shift(-4)
    df_earnings['revenue_ttm'] = df_earnings['revenue'].rolling(window=4).sum()

    if len(df_earnings) >= 8:
        for i in [4, 3]:
            _eps_est_forward = df_earnings.iloc[-i+1:]['eps_estimated'].sum()
            _eps_prev = df_earnings.iloc[-8+(5-i):-4]['eps'].sum()
            eps_est_forward_growth_rate = (float(_eps_est_forward) - float(_eps_prev)) / abs(float(_eps_prev)) if _eps_prev > 0 else None
            eps_est_forward = float(df_earnings['eps_ttm'].iloc[-i]) * (1 + eps_est_forward_growth_rate) if eps_est_forward_growth_rate else None
            df_earnings.loc[df_earnings.index[-i], 'eps_est_ttm_forward'] = eps_est_forward

    ticker = yf.Ticker(tic)
    pe_forward = ticker.info.get("forwardPE")
    current_price = ticker.info.get("currentPrice")
    implied_forward_eps = current_price / pe_forward if pe_forward and pe_forward > 0 and current_price else None
    df_earnings.loc[df_earnings.index[-2:], 'eps_est_ttm_forward'] = implied_forward_eps
    
    revenue_est_forward_growth_rate = None
    if len(df_earnings) >= 8:
        for i in [4, 3, 2]:
            _revenue_est_forward = df_earnings.iloc[-i+1:]['revenue_estimated'].sum()
            _revenue_prev = df_earnings.iloc[-8+(5-i):-4]['revenue'].sum()
            revenue_est_forward_growth_rate = (float(_revenue_est_forward) - float(_revenue_prev)) / abs(float(_revenue_prev)) if _revenue_prev > 0 else None
            revenue_est_forward = float(df_earnings['revenue_ttm'].iloc[-i]) * (1 + revenue_est_forward_growth_rate) if revenue_est_forward_growth_rate else None
            df_earnings.loc[df_earnings.index[-i], 'revenue_est_ttm_forward'] = revenue_est_forward
            
    if revenue_est_forward_growth_rate is not None:
        val = float(df_earnings['revenue_ttm'].iloc[-1]) * (1 + revenue_est_forward_growth_rate)
        df_earnings.loc[df_earnings.index[-1], 'revenue_est_ttm_forward'] = val


    df_earnings['forward_eps_growth'] = df_earnings.apply(
        lambda row: (float(row['eps_est_ttm_forward']) - float(row['eps_ttm'])) / abs(float(row['eps_ttm']))
        if pd.notna(row['eps_ttm']) and row['eps_ttm'] != 0 and pd.notna(row['eps_est_ttm_forward']) else None, axis=1
    )
    df_earnings['forward_revenue_growth'] = df_earnings.apply(
        lambda row: (float(row['revenue_est_ttm_forward']) - float(row['revenue_ttm'])) / abs(float(row['revenue_ttm']))
        if pd.notna(row['revenue_ttm']) and row['revenue_ttm'] != 0 and pd.notna(row['revenue_est_ttm_forward']) else None, axis=1
    )
    df_earnings = df_earnings.drop(columns=['eps', 'eps_ttm', 'revenue', 'revenue_ttm'])



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
    
    df['pe_forward'] = df.apply(
        lambda row: float(row['close_price']) / float(row['eps_est_ttm_forward'])
        if pd.notna(row['eps_est_ttm_forward']) and row['eps_est_ttm_forward'] > 0 else None, axis=1
    )

    df['market_cap'] = df['close_price'] * df['shares_outstanding']
    df['pe_ttm'] = df.apply(
        lambda row: float(row['close_price']) / float(row['eps_ttm'])
        if row['eps_ttm'] > 0 else None, axis=1
    )
    df['revenue_growth_yoy'] = df.apply(
        lambda row: (float(row['revenue_ttm']) - float(row['revenue_ttm_prev'])) / abs(float(row['revenue_ttm_prev']))
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_prev']) and row['revenue_ttm_prev'] != 0 else None, axis=1
    )
    df['revenue_cagr_3y'] = df.apply(
        lambda row: (float(row['revenue_ttm']) / float(row['revenue_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_3y_ago']) and row['revenue_ttm_3y_ago'] > 0 else None, axis=1
    )
    df['revenue_cagr_5y'] = df.apply(
        lambda row: (float(row['revenue_ttm']) / float(row['revenue_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['revenue_ttm']) and pd.notna(row['revenue_ttm_5y_ago']) and row['revenue_ttm_5y_ago'] > 0 else None, axis=1
    )

    df['eps_growth_yoy'] = df.apply(
        lambda row: (float(row['eps_ttm']) - float(row['eps_ttm_prev'])) / abs(float(row['eps_ttm_prev']))
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_prev']) and row['eps_ttm_prev'] != 0 else None, axis=1
    )
    df['eps_cagr_3y'] = df.apply(
        lambda row: (float(row['eps_ttm']) / float(row['eps_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_3y_ago']) and row['eps_ttm_3y_ago'] > 0 else None, axis=1
    )
    df['eps_cagr_5y'] = df.apply(
        lambda row: (float(row['eps_ttm']) / float(row['eps_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['eps_ttm']) and pd.notna(row['eps_ttm_5y_ago']) and row['eps_ttm_5y_ago'] > 0 else None, axis=1
    )

    df['fcf_growth_yoy'] = df.apply(
        lambda row: (float(row['fcf_ttm']) - float(row['fcf_ttm_prev'])) / abs(float(row['fcf_ttm_prev']))
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_prev']) and row['fcf_ttm_prev'] != 0 else None, axis=1
    )
    df['fcf_cagr_3y'] = df.apply(
        lambda row: (float(row['fcf_ttm']) / float(row['fcf_ttm_3y_ago'])) ** (1/3) - 1
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_3y_ago']) and row['fcf_ttm_3y_ago'] > 0 else None, axis=1
    )
    df['fcf_cagr_5y'] = df.apply(
        lambda row: (float(row['fcf_ttm']) / float(row['fcf_ttm_5y_ago'])) ** (1/5) - 1
        if pd.notna(row['fcf_ttm']) and pd.notna(row['fcf_ttm_5y_ago']) and row['fcf_ttm_5y_ago'] > 0 else None, axis=1
    )

    df['ebitda_growth_yoy'] = df.apply(
        lambda row: (float(row['ebitda_ttm']) - float(row['ebitda_ttm_prev'])) / abs(float(row['ebitda_ttm_prev']))
        if pd.notna(row['ebitda_ttm']) and pd.notna(row['ebitda_ttm_prev']) and row['ebitda_ttm_prev'] != 0 else None, axis=1
    )
    df['operating_income_growth_yoy'] = df.apply(
        lambda row: (float(row['operating_income_ttm']) - float(row['operating_income_ttm_prev'])) / abs(float(row['operating_income_ttm_prev']))
        if pd.notna(row['operating_income_ttm']) and pd.notna(row['operating_income_ttm_prev']) and row['operating_income_ttm_prev'] != 0 else None, axis=1
    )

    transformed_df = df[[
        'tic', 'date', 
        'revenue_growth_yoy', 'revenue_cagr_3y', 'revenue_cagr_5y', 
        'eps_growth_yoy', 'eps_cagr_3y', 'eps_cagr_5y', 
        'fcf_growth_yoy', 'fcf_cagr_3y', 'fcf_cagr_5y',
        'ebitda_growth_yoy', 'operating_income_growth_yoy',
        'forward_eps_growth', 'forward_revenue_growth'
    ]]

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
                    SELECT tic, earnings_date::date + INTERVAL '15 months' AS date
                    FROM core.balance_sheets 
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
