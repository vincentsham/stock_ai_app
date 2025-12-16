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
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
            total_assets, total_debt, total_stockholders_equity, 
            cash_and_short_term_investments, cash_and_cash_equivalents
        FROM core.balance_sheets 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               eps_diluted, revenue, ebitda, 
               weighted_average_shs_out_dil AS shares_outstanding
        FROM core.income_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')
    df_income['eps_ttm'] = df_income['eps_diluted'].rolling(window=4).sum()
    df_income['eps_ttm_prev'] = df_income['eps_ttm'].shift(4) 
    df_income['revenue_ttm'] = df_income['revenue'].rolling(window=4).sum()
    df_income['ebitda_ttm'] = df_income['ebitda'].rolling(window=4).sum()

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

    earnings_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, 
               eps, eps_estimated
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

    for i in [4, 3]:
        _eps_est_forward = df_earnings.iloc[-i+1:]['eps_estimated'].sum()
        _eps_prev = df_earnings.iloc[-8+(5-i):-4]['eps'].sum()
        eps_est_forward_growth_rate = (float(_eps_est_forward) - float(_eps_prev)) / abs(float(_eps_prev)) if _eps_prev > 0 else None
        eps_est_forward = float(df['eps_ttm'].iloc[-i]) * (1 + eps_est_forward_growth_rate) if eps_est_forward_growth_rate else None
        df_earnings.loc[df_earnings.index[-i], 'eps_est_ttm_forward'] = eps_est_forward

    ticker = yf.Ticker(tic)
    pe_forward = ticker.info.get("forwardPE")
    current_price = ticker.info.get("currentPrice")
    df_earnings.iloc[-2:]['eps_est_ttm_forward'] = current_price / pe_forward if pe_forward and pe_forward > 0 and current_price else None   
    # df_earnings.iloc[-4:]['eps_est_ttm_forward'] = current_price / pe_forward if pe_forward and pe_forward > 0 and current_price else None   
    
    df_earnings = df_earnings.drop(columns=['eps', 'eps_ttm'])
 

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
            direction="forward",
            allow_exact_matches=True
        )
    df = df.drop(columns=['earnings_date', 'calendar_year', 'calendar_quarter'])
    
    df['pe_forward'] = df.apply(
        lambda row: float(row['close_price']) / float(row['eps_est_ttm_forward'])
        if row['eps_est_ttm_forward'] > 0 else None, axis=1
    )
  
    df['market_cap'] = df['close_price'] * df['shares_outstanding']
    df['book_value_per_share'] = df['total_stockholders_equity'] / df['shares_outstanding']
    df['ev'] = df['market_cap'] + df['total_debt'] - df['cash_and_short_term_investments']

    df['pe_ttm'] = df.apply(
        lambda row: float(row['close_price']) / float(row['eps_ttm'])
        if row['eps_ttm'] > 0 else None, axis=1
    )
    df['ev_to_ebitda_ttm'] = df.apply(
        lambda row: float(row['ev']) / float(row['ebitda_ttm'])
        if row['ev'] and row['ebitda_ttm'] > 0 else None, axis=1
    )
    df['ps_ttm'] = df.apply(
        lambda row: (float(row['close_price']) * float(row['shares_outstanding'])) / float(row['revenue_ttm'])
        if row['revenue_ttm'] > 0 else None, axis=1
    )
    df['p_to_fcf_ttm'] = df.apply(
        lambda row: (float(row['close_price']) * float(row['shares_outstanding'])) / float(row['fcf_ttm'])
        if row['fcf_ttm'] > 0 else None, axis=1
    )
    df['fcf_yield_ttm'] = df.apply(
        lambda row: float(row['fcf_ttm']) / float(row['market_cap'])
        if row['fcf_ttm'] > 0 else None, axis=1
    )
    df['ev_to_revenue_ttm'] = df.apply(
        lambda row: float(row['ev']) / float(row['revenue_ttm'])
        if row['ev'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['eps_growth_rate'] = df.apply(
        lambda r: (r['eps_ttm'] - r['eps_ttm_prev']) / abs(r['eps_ttm_prev'])
        if pd.notna(r['eps_ttm']) and pd.notna(r['eps_ttm_prev']) and r['eps_ttm_prev'] != 0
        else None,
        axis=1
    )
    df['peg_ratio'] = df.apply(
        lambda row: float(row['pe_ttm']) / (float(row['eps_growth_rate']) * 100)
        if row['eps_growth_rate'] and row['eps_growth_rate'] > 0 and row['pe_ttm'] else None, axis=1
    )
    df['price_to_book'] = df.apply(
        lambda row: float(row['close_price']) / float(row['book_value_per_share'])
        if row['book_value_per_share'] and row['book_value_per_share'] > 0 else None, axis=1
    )
    df['ev_to_fcf_ttm'] = df.apply(
        lambda row: float(row['ev']) / float(row['fcf_ttm'])
        if row['ev'] and row['fcf_ttm'] > 0 else None, axis=1
    )
    df['earnings_yield_ttm'] = df.apply(
        lambda row: float(row['eps_ttm']) / float(row['close_price']), axis=1
    )
    df['revenue_yield_ttm'] = df.apply(
        lambda row: float(row['revenue_ttm']) / float(row['market_cap'])
        if row['revenue_ttm'] > 0 else None, axis=1
    )

    transformed_df = df[[
        'tic', 'date', 'market_cap', 'pe_ttm', 'pe_forward', 'ev_to_ebitda_ttm',
        'ps_ttm', 'p_to_fcf_ttm', 'fcf_yield_ttm', 'ev_to_revenue_ttm',
        'peg_ratio', 'price_to_book', 'ev_to_fcf_ttm',  'earnings_yield_ttm',
        'revenue_yield_ttm'
    ]]
    return transformed_df




def load_records(transformed_df, conn):

    # Insert records into core.valuation_metrics
    total_records = insert_records(conn, transformed_df, 'core.valuation_metrics', ['tic', 'date'])
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
