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
            total_debt, total_stockholders_equity, cash_and_short_term_investments
        FROM core.balance_sheets 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')

    df_balance_sheet['total_assets_avg'] = (df_balance_sheet['total_assets'] + df_balance_sheet['total_assets'].shift(4)) / 2
    df_balance_sheet['total_stockholders_equity_avg'] = (df_balance_sheet['total_stockholders_equity'] + df_balance_sheet['total_stockholders_equity'].shift(4)) / 2

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               eps_diluted, revenue, ebit, ebitda, gross_profit, net_income,
               income_tax_expense, income_before_tax
        FROM core.income_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')
    df_income['revenue_ttm'] = df_income['revenue'].rolling(window=4).sum()
    df_income['ebitda_ttm'] = df_income['ebitda'].rolling(window=4).sum()
    df_income['ebit_ttm'] = df_income['ebit'].rolling(window=4).sum()
    df_income['gross_profit_ttm'] = df_income['gross_profit'].rolling(window=4).sum()
    df_income['net_income_ttm'] = df_income['net_income'].rolling(window=4).sum()


    cash_flow_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               free_cash_flow as fcf, operating_cash_flow as ocf
        FROM core.cash_flow_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_cash_flow = read_sql_query(cash_flow_statement_query, conn)
    df_cash_flow['earnings_date'] = pd.to_datetime(df_cash_flow['earnings_date'])
    df_cash_flow = df_cash_flow.sort_values('earnings_date')
    df_cash_flow['fcf_ttm'] = df_cash_flow['fcf'].rolling(window=4).sum()
    df_cash_flow['ocf_ttm'] = df_cash_flow['ocf'].rolling(window=4).sum()


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

    # Compute metrics
    df['gross_margin'] = df.apply(
        lambda row: float(row['gross_profit_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['operating_margin'] = df.apply(
        lambda row: float(row['ebit_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['ebitda_margin'] = df.apply(
        lambda row: float(row['ebitda_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['net_margin'] = df.apply(
        lambda row: float(row['net_income_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['roa'] = df.apply(
        lambda row: float(row['net_income_ttm']) / float(row['total_assets_avg'])
        if row['total_assets_avg'] and row['total_assets_avg'] > 0 else None, axis=1
    )
    df['roe'] = df.apply(
        lambda row: float(row['net_income_ttm']) / float(row['total_stockholders_equity_avg'])
        if row['total_stockholders_equity_avg'] and row['total_stockholders_equity_avg'] > 0 else None, axis=1
    )
    df['ocf_margin'] = df.apply(
        lambda row: float(row['ocf_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )
    df['fcf_margin'] = df.apply(
        lambda row: float(row['fcf_ttm']) / float(row['revenue_ttm'])
        if row['revenue_ttm'] and row['revenue_ttm'] > 0 else None, axis=1
    )

    transformed_df = df[['tic', 'date', 'gross_margin', 'operating_margin', 'ebitda_margin',
                         'net_margin', 'roa', 'roe', 'ocf_margin', 'fcf_margin']]   
    return transformed_df




def load_records(transformed_df, conn):

    # Insert records into core.profitability_metrics
    total_records = insert_records(conn, transformed_df, 'core.profitability_metrics', ['tic', 'date'])
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
