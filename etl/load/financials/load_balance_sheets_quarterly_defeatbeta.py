from curses import raw
from numpy import record
import pandas as pd
import json
from database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.balance_sheets table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT 
        i.tic, 
        c.calendar_year,
        c.calendar_quarter,
        c.earnings_date,
        c.fiscal_year, 
        c.fiscal_quarter, 
        c.fiscal_date,
        i.source, 
        i.raw_json, 
        i.raw_json_sha256 
    FROM raw.balance_sheets_quarterly as i
    INNER JOIN core.earnings_calendar as c
    ON i.tic = c.tic AND ABS(i.fiscal_date::DATE - c.fiscal_date::DATE) <= 15
    LEFT JOIN core.balance_sheets_quarterly AS ci
    ON c.tic = ci.tic AND c.fiscal_year = ci.fiscal_year AND c.fiscal_quarter = ci.fiscal_quarter
    WHERE i.source = 'defeatbeta'
        AND (ci.raw_json_sha256 IS NULL 
                OR i.raw_json_sha256 IS DISTINCT FROM ci.raw_json_sha256);
    """

    # Connect to the database
    df = execute_query(query)

    return df


def transform_records(raw_df):
    """
    Transforms the raw balance sheet data to match the schema of core.balance_sheets.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw balance sheet data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.balance_sheets schema.
    """
    transformed_df = pd.DataFrame()

    # Map columns from raw to core schema
    for i in range(len(raw_df)):

        data = raw_df.iloc[i]['raw_json']

        transformed_df.at[i, 'tic'] = raw_df.iloc[i]['tic']
        transformed_df.at[i, 'calendar_year'] = raw_df.iloc[i]['calendar_year']
        transformed_df.at[i, 'calendar_quarter'] = raw_df.iloc[i]['calendar_quarter']
        transformed_df.at[i, 'earnings_date'] = raw_df.iloc[i]['earnings_date']
        transformed_df.at[i, 'fiscal_year'] = raw_df.iloc[i]['fiscal_year']
        transformed_df.at[i, 'fiscal_quarter'] = raw_df.iloc[i]['fiscal_quarter']
        transformed_df.at[i, 'fiscal_date'] = raw_df.iloc[i]['fiscal_date']

        """
        balance_sheet_mapping = {
            # --- Assets ---
            "Total Assets": "total_assets",
            "Total Current Assets": "total_current_assets",
            "Cash, Cash Equivalents & Short Term Investments": "cash_and_short_term_investments",
            "Cash And Cash Equivalents": "cash_and_cash_equivalents",
            "Receivables": "accounts_receivable",
            
            # Inventory Deep Dive (Important for Hardware companies like NVDA)
            "Inventory": "inventory",
            "Raw Materials": "inventory_raw_materials",
            "Work in Process": "inventory_work_in_process",
            "Finished Goods": "inventory_finished_goods",
            
            # Long Term Assets
            "Net PPE": "net_ppe",
            "Goodwill And Other Intangible Assets": "goodwill_and_intangibles",

            # --- Liabilities ---
            "Total Liabilities": "total_liabilities",
            "Total Current Liabilities": "total_current_liabilities",
            "Accounts Payable": "accounts_payable",
            "Total Debt": "total_debt",
            "Long Term Debt": "long_term_debt",
            "Current Debt And Capital Lease Obligation": "current_debt_and_capital_lease",
            
            # Deferred Revenue (The "Backlog" Proxy)
            "Current Deferred Revenue": "deferred_revenue_current",
            "Non Current Deferred Revenue": "deferred_revenue_non_current",

            # --- Equity ---
            "Total Equity": "total_equity",
            "Retained Earnings": "retained_earnings",
            "Common Stock": "common_stock",

            # --- Metrics ---
            "Working Capital": "working_capital",
            "Invested Capital": "invested_capital",
            "Net Tangible Assets": "net_tangible_assets",
            "Ordinary Shares Number": "ordinary_shares_number"
        }

        """

        # Assets
        transformed_df.at[i, "total_assets"] = data.get('Total Assets', None)
        transformed_df.at[i, "total_current_assets"] = data.get('Total Current Assets', None)
        transformed_df.at[i, "cash_and_short_term_investments"] = data.get('Cash, Cash Equivalents & Short Term Investments', None)
        transformed_df.at[i, "cash_and_cash_equivalents"] = data.get('Cash And Cash Equivalents', None)
        transformed_df.at[i, "accounts_receivable"] = data.get('Receivables', None)


        transformed_df.at[i, "inventory"] = data.get('Inventory', None)

        transformed_df.at[i, "net_ppe"] = data.get('Net PPE', None)
        transformed_df.at[i, "goodwill_and_intangibles"] = data.get('Goodwill And Other Intangible Assets', None)

        # Liabilities
        transformed_df.at[i, "total_liabilities"] = data.get('Total Liabilities', None)
        transformed_df.at[i, "total_current_liabilities"] = data.get('Total Current Liabilities', None)
        transformed_df.at[i, "accounts_payable"] = data.get('Accounts Payable', None)
        transformed_df.at[i, "deferred_revenue_current"] = data.get('Current Deferred Revenue', None)
        transformed_df.at[i, "deferred_revenue_non_current"] = data.get('Non Current Deferred Revenue', None)

        # Debt
        transformed_df.at[i, "total_debt"] = data.get('Total Debt', None)
        transformed_df.at[i, "long_term_debt"] = data.get('Long Term Debt', None)
        transformed_df.at[i, "current_debt_and_capital_lease"] = data.get('Current Debt And Capital Lease Obligation', None)

        # Equity
        transformed_df.at[i, "total_equity"] = data.get('Total Equity', None)
        transformed_df.at[i, "retained_earnings"] = data.get('Retained Earnings', None)
        transformed_df.at[i, "common_stock"] = data.get('Common Stock', None)

        # Metrics
        transformed_df.at[i, "working_capital"] = data.get('Working Capital', None)
        transformed_df.at[i, "invested_capital"] = data.get('Invested Capital', None)
        transformed_df.at[i, "net_tangible_assets"] = data.get('Net Tangible Assets', None)
        transformed_df.at[i, "ordinary_shares_number"] = data.get('Ordinary Shares Number', None)



        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.balance_sheets_quarterly table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.balance_sheets_quarterly schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.balance_sheets_quarterly
        total_records = insert_records(conn, transformed_df, 'core.balance_sheets_quarterly', ['tic', 'calendar_year', 'calendar_quarter'])
        print(f"Total records inserted/updated in core.balance_sheets_quarterly: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for balance sheets.
    """
    # Step 1: Read raw income statements
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.balance_sheets
    load_records(transformed_df)

if __name__ == "__main__":
    main()