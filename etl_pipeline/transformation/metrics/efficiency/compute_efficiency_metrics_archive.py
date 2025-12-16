from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf



def transform_records(conn, tic: str, date: str) -> pd.DataFrame:
    market_cap_query = f"""
        SELECT tic, market_cap, employees
        FROM core.stock_profiles
        WHERE tic = '{tic}'
        LIMIT 1;
    """
    df_market_cap = read_sql_query(market_cap_query, conn)
    employees = df_market_cap.at[0, 'employees'] if not df_market_cap.empty else None

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
            property_plant_equipment_net, accounts_receivables, account_payables, inventory
        FROM core.balance_sheets 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')

    df_balance_sheet['total_assets_avg'] = (df_balance_sheet['total_assets'] + df_balance_sheet.shift(4)['total_assets']) / 2
    df_balance_sheet['property_plant_equipment_net_avg'] = (df_balance_sheet['property_plant_equipment_net'] + df_balance_sheet.shift(4)['property_plant_equipment_net']) / 2
    df_balance_sheet['accounts_receivables_avg'] = (df_balance_sheet['accounts_receivables'] + df_balance_sheet.shift(4)['accounts_receivables']) / 2
    df_balance_sheet['accounts_payables_avg'] = (df_balance_sheet['account_payables'] + df_balance_sheet.shift(4)['account_payables']) / 2
    df_balance_sheet['inventory_avg'] = (df_balance_sheet['inventory'] + df_balance_sheet.shift(4)['inventory']) / 2

    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               eps, revenue, ebit, ebitda, gross_profit, 
               net_income, operating_expenses, cost_of_revenue,
               income_tax_expense, income_before_tax
        FROM core.income_statements 
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')

    df_income['revenue_ttm'] = df_income['revenue'].rolling(window=4).sum()
    df_income['operating_expenses_ttm'] = df_income['operating_expenses'].rolling(window=4).sum()
    df_income['cost_of_revenue_ttm'] = df_income['cost_of_revenue'].rolling(window=4).sum()

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

    df['asset_turnover'] = df.apply(
        lambda row: row['revenue_ttm'] / row['total_assets_avg']
        if row['total_assets_avg'] and row['total_assets_avg'] != 0 else None, axis=1
    )
    df['fixed_asset_turnover'] = df.apply(
        lambda row: row['revenue_ttm'] / row['property_plant_equipment_net_avg']
        if row['property_plant_equipment_net_avg'] and row['property_plant_equipment_net_avg'] != 0 else None, axis=1
    )
    df['revenue_per_employee'] = df.apply(
        lambda row: row['revenue_ttm'] / employees
        if employees and employees != 0 else None, axis=1
    )
    df['opex_ratio'] = df.apply(
        lambda row: row['operating_expenses_ttm'] / row['revenue_ttm']
        if row['revenue_ttm'] and row['revenue_ttm'] != 0 else None, axis=1
    )
    df['dso'] = df.apply(
        lambda row: (row['accounts_receivables_avg'] / row['revenue_ttm']) * 365
        if row['accounts_receivables_avg'] and row['revenue_ttm'] and row['revenue_ttm'] != 0 else None, axis=1
    )
    df['dio'] = df.apply(
        lambda row: (row['inventory_avg'] / row['cost_of_revenue_ttm']) * 365
        if row['inventory_avg'] and row['cost_of_revenue_ttm'] and row['cost_of_revenue_ttm'] != 0 else None, axis=1
    )
    df['dpo'] = df.apply(
        lambda row: (row['accounts_payables_avg'] / row['cost_of_revenue_ttm']) * 365
        if row['accounts_payables_avg'] and row['cost_of_revenue_ttm'] and row['cost_of_revenue_ttm'] != 0 else None, axis=1
    )
    df['cash_conversion_cycle'] = df.apply(
        lambda row: row['dso'] + row['dio'] - row['dpo']
        if row['dso'] is not None and row['dio'] is not None and row['dpo'] is not None else None, axis=1
    )

    
    transformed_df = df[['tic', 'date', 'asset_turnover', 'fixed_asset_turnover',
                         'revenue_per_employee', 'opex_ratio', 'dso', 'dio',
                         'dpo', 'cash_conversion_cycle']]

    return transformed_df




def load_records(transformed_df, conn):

    # Insert records into core.efficiency_metrics
    total_records = insert_records(conn, transformed_df, 'core.efficiency_metrics', ['tic', 'date'])
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
