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
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date, total_assets,
            total_debt, total_equity, cash_and_short_term_investments,
            inventory, retained_earnings, total_current_assets,
            total_current_liabilities, total_liabilities
        FROM core.balance_sheets_quarterly
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_balance_sheet = read_sql_query(balance_sheet_query, conn)
    df_balance_sheet['earnings_date'] = pd.to_datetime(df_balance_sheet['earnings_date'])
    df_balance_sheet = df_balance_sheet.sort_values('earnings_date')
    df_balance_sheet = convert_decimals_to_float(df_balance_sheet)

    df_balance_sheet['total_debt_avg'] = (df_balance_sheet['total_debt'] + df_balance_sheet['total_debt'].shift(4)) / 2
    df_balance_sheet['total_assets_avg'] = (df_balance_sheet['total_assets'] + df_balance_sheet['total_assets'].shift(4)) / 2
    df_balance_sheet['total_equity_avg'] = (df_balance_sheet['total_equity'] + df_balance_sheet['total_equity'].shift(4)) / 2
    df_balance_sheet['cash_and_short_term_investments_avg'] = (df_balance_sheet['cash_and_short_term_investments'] + df_balance_sheet['cash_and_short_term_investments'].shift(4)) / 2
    df_balance_sheet['net_debt_avg'] = df_balance_sheet['total_debt_avg'] - df_balance_sheet['cash_and_short_term_investments_avg']
    df_balance_sheet['total_current_assets_avg'] = (df_balance_sheet['total_current_assets'] + df_balance_sheet['total_current_assets'].shift(4)) / 2
    df_balance_sheet['total_current_liabilities_avg'] = (df_balance_sheet['total_current_liabilities'] + df_balance_sheet['total_current_liabilities'].shift(4)) / 2
    df_balance_sheet['total_liabilities_avg'] = (df_balance_sheet['total_liabilities'] + df_balance_sheet['total_liabilities'].shift(4)) / 2
    df_balance_sheet['retained_earnings_avg'] = (df_balance_sheet['retained_earnings'] + df_balance_sheet['retained_earnings'].shift(4)) / 2



    income_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               eps, revenue, ebit, ebitda, gross_profit, 
               net_income, operating_expenses, cost_of_revenue,
               income_tax_expense, income_before_tax, interest_expense
        FROM core.income_statements_quarterly
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_income = read_sql_query(income_statement_query, conn)
    df_income['earnings_date'] = pd.to_datetime(df_income['earnings_date'])
    df_income = df_income.sort_values('earnings_date')
    df_income = convert_decimals_to_float(df_income)

    df_income['revenue_ttm'] = df_income['revenue'].rolling(window=4).sum()
    df_income['ebit_ttm'] = df_income['ebit'].rolling(window=4).sum()
    df_income['ebitda_ttm'] = df_income['ebitda'].rolling(window=4).sum()
    df_income['interest_expense_ttm'] = df_income['interest_expense'].rolling(window=4).sum()
    

    cash_flow_statement_query = f"""
        SELECT tic, calendar_year, calendar_quarter, earnings_date::date,
               free_cash_flow as fcf, operating_cash_flow as ocf
        FROM core.cash_flow_statements_quarterly
        WHERE tic = '{tic}'
        ORDER BY earnings_date;
    """
    df_cash_flow = read_sql_query(cash_flow_statement_query, conn)
    df_cash_flow['earnings_date'] = pd.to_datetime(df_cash_flow['earnings_date'])
    df_cash_flow = df_cash_flow.sort_values('earnings_date')
    df_cash_flow = convert_decimals_to_float(df_cash_flow)

    df_cash_flow['fcf_ttm'] = df_cash_flow['fcf'].rolling(window=4).sum()


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

    df['net_debt_to_ebitda_ttm'] = df.apply(
        lambda row: float(row['net_debt_avg']) / float(row['ebitda_ttm'])
        if pd.notna(row['net_debt_avg']) and pd.notna(row['ebitda_ttm']) and row['ebitda_ttm'] != 0 else np.nan, axis=1
    )
    df['interest_coverage_ttm'] = df.apply(
        lambda row: float(row['ebit_ttm']) / abs(float(row['interest_expense_ttm']))
        if pd.notna(row['ebit_ttm']) and pd.notna(row['interest_expense_ttm']) and row['interest_expense_ttm'] != 0 else np.nan, axis=1
    )
    df['current_ratio'] = df.apply(
        lambda row: float(row['total_current_assets_avg']) / float(row['total_current_liabilities_avg'])
        if pd.notna(row['total_current_assets_avg']) and pd.notna(row['total_current_liabilities_avg']) and row['total_current_liabilities_avg'] != 0 else np.nan, axis=1
    )
    df['quick_ratio'] = df.apply(
        lambda row: (float(row['total_current_assets_avg']) - float(row['inventory'])) / float(row['total_current_liabilities_avg'])
        if pd.notna(row['total_current_assets_avg']) and pd.notna(row['inventory']) and pd.notna(row['total_current_liabilities_avg']) and row['total_current_liabilities_avg'] != 0 else np.nan, axis=1
    )
    df['cash_ratio'] = df.apply(
        lambda row: float(row['cash_and_short_term_investments_avg']) / float(row['total_current_liabilities_avg'])
        if pd.notna(row['cash_and_short_term_investments_avg']) and pd.notna(row['total_current_liabilities_avg']) and row['total_current_liabilities_avg'] != 0 else np.nan, axis=1
    )


    df['debt_to_equity'] = df.apply(
        lambda row: float(row['total_debt_avg']) / float(row['total_equity_avg'])
        if pd.notna(row['total_debt_avg']) and pd.notna(row['total_equity_avg']) and row['total_equity_avg'] > 0 else np.nan, axis=1
    )
    df['debt_to_assets'] = df.apply(
        lambda row: float(row['total_debt_avg']) / float(row['total_assets_avg'])
        if pd.notna(row['total_debt_avg']) and pd.notna(row['total_assets_avg']) and row['total_assets_avg'] != 0 else np.nan, axis=1
    )

    df['A'] = df.apply(
        lambda r: (float(r['total_current_assets_avg']) - float(r['total_current_liabilities_avg'])) / float(r['total_assets_avg'])
        if pd.notna(r['total_current_assets_avg']) and pd.notna(r['total_current_liabilities_avg']) and pd.notna(r['total_assets_avg']) and r['total_assets_avg'] != 0 else np.nan,
        axis=1,
    )
    df['B'] = df.apply(
        lambda r: float(r['retained_earnings_avg']) / float(r['total_assets_avg'])
        if pd.notna(r['retained_earnings_avg']) and pd.notna(r['total_assets_avg']) and r['total_assets_avg'] != 0 else np.nan,
        axis=1,
    )
    df['C'] = df.apply(
        lambda r: float(r['ebit_ttm']) / float(r['total_assets_avg'])
        if pd.notna(r['ebit_ttm']) and pd.notna(r['total_assets_avg']) and r['total_assets_avg'] != 0 else np.nan,
        axis=1,
    )
    df['D'] = df.apply(
        lambda r: float(r['total_equity_avg']) / float(r['total_liabilities_avg'])
        if pd.notna(r['total_equity_avg']) and pd.notna(r['total_liabilities_avg']) and r['total_liabilities_avg'] != 0 else np.nan,
        axis=1,
    )
    df['E'] = df.apply(
        lambda r: float(r['revenue_ttm']) / float(r['total_assets_avg'])
        if pd.notna(r['revenue_ttm']) and pd.notna(r['total_assets_avg']) and r['total_assets_avg'] != 0 else np.nan,
        axis=1,
    )

    df['altman_z_score'] = df.apply(
        lambda r: (1.2 * float(r['A'])) + (1.4 * float(r['B'])) + (3.3 * float(r['C'])) + (0.6 * float(r['D'])) + (1.0 * float(r['E']))
        if pd.notna(r['A']) and pd.notna(r['B']) and pd.notna(r['C']) and pd.notna(r['D']) and pd.notna(r['E']) else np.nan,
        axis=1,
    )

    df['cash_runway_months'] = df.apply(
        lambda row: float(row['cash_and_short_term_investments_avg']) / (abs(float(row['fcf_ttm'])) / 12)
        if pd.notna(row['cash_and_short_term_investments_avg']) and pd.notna(row['fcf_ttm']) and row['fcf_ttm'] < 0 else np.nan, axis=1
    )  

    transformed_df = df[['tic', 'date','net_debt_to_ebitda_ttm',
                         'interest_coverage_ttm', 'current_ratio', 'quick_ratio',
                         'cash_ratio', 'debt_to_equity', 'debt_to_assets', 'altman_z_score',
                         'cash_runway_months'
                         ]]

    return transformed_df


def load_records(transformed_df, conn):

    # Insert records into core.financial_health_metrics table
    total_records = insert_records(conn, transformed_df, 'core.financial_health_metrics', ['tic', 'date'])
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
