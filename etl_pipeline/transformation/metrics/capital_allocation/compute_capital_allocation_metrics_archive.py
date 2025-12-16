from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf



def transform_records(conn, tic: str, date: str) -> pd.DataFrame:
    market_cap_query = f"""
        SELECT tic, market_cap
        FROM core.stock_profiles
        WHERE tic = '{tic}'
        LIMIT 1;
    """
    df_market_cap = read_sql_query(market_cap_query, conn)
    market_cap = df_market_cap.at[0, 'market_cap'] if not df_market_cap.empty else None

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
            total_debt, total_stockholders_equity, cash_and_short_term_investments,
            property_plant_equipment_net, accounts_receivables, 
            inventory, total_current_assets, retained_earnings,
            total_current_liabilities, total_liabilities
        FROM core.balance_sheets 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')

    df_balance_sheet['total_assets_avg'] = (df_balance_sheet['total_assets'] + df_balance_sheet['total_assets'].shift(4)) / 2
    df_balance_sheet['total_debt_avg'] = (df_balance_sheet['total_debt'] + df_balance_sheet['total_debt'].shift(4)) / 2
    df_balance_sheet['total_stockholders_equity_avg'] = (df_balance_sheet['total_stockholders_equity'] + df_balance_sheet['total_stockholders_equity'].shift(4)) / 2
    df_balance_sheet['cash_and_short_term_investments_avg'] = (df_balance_sheet['cash_and_short_term_investments'] + df_balance_sheet['cash_and_short_term_investments'].shift(4)) / 2
    df_balance_sheet['ic'] = (df_balance_sheet['total_debt_avg'] + df_balance_sheet['total_stockholders_equity_avg'] - df_balance_sheet['cash_and_short_term_investments_avg'])

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               eps, revenue, ebit, ebitda, gross_profit, 
               net_income, operating_expenses, cost_of_revenue,
               income_tax_expense, income_before_tax, interest_expense,
               weighted_average_shs_out_dil AS shares_outstanding
        FROM core.income_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')
    df_income['ebit_ttm'] = df_income['ebit'].rolling(window=4).sum()
    df_income['income_tax_expense_ttm'] = df_income['income_tax_expense'].rolling(window=4).sum()
    df_income['income_before_tax_ttm'] = df_income['income_before_tax'].rolling(window=4).sum()
    df_income['shares_outstanding_prev'] = df_income['shares_outstanding'].shift(4)
    df_income['share_count_change_yoy'] = (df_income['shares_outstanding'] - df_income['shares_outstanding_prev']) / df_income['shares_outstanding_prev']
    df_income['tax_rate'] = df_income.apply(
        lambda row: (float(row['income_tax_expense_ttm']) / float(row['income_before_tax_ttm']))
        if pd.notna(row['income_before_tax_ttm']) and row['income_before_tax_ttm'] > 0 else 0.21, axis=1
    )
    df_income['tax_rate'] = df_income['tax_rate'].clip(lower=0, upper=0.4)
    df_income['nopat'] = df_income['ebit_ttm'] * (1 - df_income['tax_rate'])

    cash_flow_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               free_cash_flow as fcf, operating_cash_flow as ocf,
               net_common_stock_issuance, common_dividends_paid,
               capital_expenditure, change_in_working_capital
        FROM core.cash_flow_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_cash_flow = read_sql_query(cash_flow_statement_query, conn)
    df_cash_flow['earnings_date'] = pd.to_datetime(df_cash_flow['earnings_date'])
    df_cash_flow = df_cash_flow.sort_values('earnings_date')
    df_cash_flow['fcf_ttm'] = df_cash_flow['fcf'].rolling(window=4).sum()
    df_cash_flow['fcf_ttm_prev'] = df_cash_flow['fcf_ttm'].shift(4)
    df_cash_flow['net_common_stock_issuance_ttm'] = (-df_cash_flow['net_common_stock_issuance'].rolling(window=4).sum()).clip(lower=0)
    df_cash_flow['net_common_dividends_paid_ttm'] = (-df_cash_flow['common_dividends_paid'].rolling(window=4).sum()).clip(lower=0)
    df_cash_flow['capital_expenditure_ttm'] = (-df_cash_flow['capital_expenditure'].rolling(window=4).sum()).clip(lower=0)
    df_cash_flow['change_in_working_capital_ttm'] = df_cash_flow['change_in_working_capital'].rolling(window=4).sum()


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

    df['roic'] = df.apply(
        lambda row: float(row['nopat']) / float(row['ic'])
        if pd.notna(row['ic']) and row['ic'] > 0 else None, axis=1
    )
    df['total_shareholder_yield'] = df.apply(
        lambda row: (float(row['net_common_dividends_paid_ttm']) + float(row['net_common_stock_issuance_ttm'])) / float(market_cap)
        if pd.notna(market_cap) and market_cap > 0 else None, axis=1
    )
    df['share_count_change_yoy'] = df['share_count_change_yoy']
    df['reinvestment_rate'] = df.apply(
        lambda row: (float(row['capital_expenditure_ttm']) + float(row['change_in_working_capital_ttm'])) / float(row['nopat'])
        if pd.notna(row['nopat']) and row['nopat'] > 0 else None, axis=1
    )
    df['fcf_per_share'] = df.apply(
        lambda row: float(row['fcf_ttm']) / float(row['shares_outstanding'])
        if pd.notna(row['shares_outstanding']) and row['shares_outstanding'] > 0 else None, axis=1
    )
    df['fcf_per_share_prev'] = df.apply(
        lambda row: float(row['fcf_ttm_prev']) / float(row['shares_outstanding_prev'])
        if pd.notna(row['fcf_ttm_prev']) and pd.notna(row['shares_outstanding_prev']) and row['shares_outstanding_prev'] > 0 else None, axis=1
    )
    df['fcf_per_share_growth_yoy'] = df.apply(
        lambda row: (float(row['fcf_per_share']) - float(row['fcf_per_share_prev'])) / float(row['fcf_per_share_prev'])
        if pd.notna(row['fcf_per_share_prev']) and row['fcf_per_share_prev'] > 0 else None, axis=1
    )

    transformed_df = df[['tic', 'date', 'roic', 'total_shareholder_yield',
                         'share_count_change_yoy', 'reinvestment_rate',
                         'fcf_per_share_growth_yoy']]

    return transformed_df




def load_records(transformed_df, conn):

    # Insert records into core.capital_allocation_metrics table
    total_records = insert_records(conn, transformed_df, 'core.capital_allocation_metrics', ['tic', 'date'])
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
