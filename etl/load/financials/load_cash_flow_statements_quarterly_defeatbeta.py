import pandas as pd
import json
from database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.cash_flow_statements table and returns it as a pandas DataFrame.
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
    FROM raw.cash_flow_statements_quarterly as i
    INNER JOIN core.earnings_calendar as c
    ON i.tic = c.tic AND ABS(i.fiscal_date::DATE - c.fiscal_date::DATE) <= 15
    LEFT JOIN core.cash_flow_statements_quarterly AS ci
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
    Transforms the raw cash flow statements data to match the schema of core.cash_flow_statements_quarterly.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw cash flow statements data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.cash_flow_statements_quarterly schema.
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
        cash_flow_mapping = {
            # --- Operating Activities ---
            "Net Income from Continuing Operations": "net_income",
            "Operating Cash Flow": "operating_cash_flow",
            "Depreciation & Amortization": "depreciation_amortization",
            "Deferred Income Tax": "deferred_income_tax",
            "Stock Based Compensation": "stock_based_compensation",
            
            # Working Capital Components
            "Change In Working Capital": "change_in_working_capital",
            "Changes in Account Receivables": "change_in_receivables",
            "Change in Inventory": "change_in_inventory",
            "Change in Account Payable": "change_in_accounts_payable",

            # --- Investing Activities ---
            "Investing Cash Flow": "investing_cash_flow",
            "Purchase of PPE": "capital_expenditure",  # Critical for FCF calculation
            "Purchase of Business": "acquisitions_net",
            "Purchase of Investment": "investments_purchases",
            "Sale of Investment": "investments_sales",

            # --- Financing Activities ---
            "Financing Cash Flow": "financing_cash_flow",
            "Repayment of Debt": "debt_repayment",
            "Long Term Debt Issuance": "debt_issuance",
            "Repurchase of Capital Stock": "common_stock_repurchased",
            "Cash Dividends Paid": "dividends_paid",

            # --- Summary & Supplemental ---
            "Free Cash Flow": "free_cash_flow",
            "End Cash Position": "end_cash_position",
            "Changes in Cash": "net_change_in_cash",
            "Income Tax Paid Supplemental Data": "income_tax_paid",
            "Interest Paid Supplemental Data": "interest_paid"
        }
        """

        transformed_df.at[i, 'net_income'] = data.get('Net Income from Continuing Operations', None)
        transformed_df.at[i, 'operating_cash_flow'] = data.get('Operating Cash Flow', None)
        transformed_df.at[i, 'depreciation_amortization'] = data.get('Depreciation & Amortization', None)
        transformed_df.at[i, 'deferred_income_tax'] = data.get('Deferred Income Tax', None)
        transformed_df.at[i, 'stock_based_compensation'] = data.get('Stock Based Compensation', None)

        transformed_df.at[i, 'change_in_working_capital'] = data.get('Change In Working Capital', None)
        transformed_df.at[i, 'change_in_receivables'] = data.get('Changes in Account Receivables', None)
        transformed_df.at[i, 'change_in_inventory'] = data.get('Change in Inventory', None)
        transformed_df.at[i, 'change_in_accounts_payable'] = data.get('Change in Account Payable', None)

        transformed_df.at[i, 'investing_cash_flow'] = data.get('Investing Cash Flow', None)
        transformed_df.at[i, 'capital_expenditure'] = data.get('Purchase of PPE', None)
        transformed_df.at[i, 'acquisitions_net'] = data.get('Purchase of Business', None)
        transformed_df.at[i, 'investments_purchases'] = data.get('Purchase of Investment', None)
        transformed_df.at[i, 'investments_sales'] = data.get('Sale of Investment', None)

        transformed_df.at[i, 'financing_cash_flow'] = data.get('Financing Cash Flow', None)
        
        debt_issued = data.get('Long Term Debt Issuance', None)
        debt_repaid = data.get('Long Term Debt Payments', None)
        if debt_issued is not None or debt_repaid is not None:
            net_debt_issuance = (debt_issued or 0) - (debt_repaid or 0)
            transformed_df.at[i, 'net_debt_issuance'] = net_debt_issuance
        else:
            transformed_df.at[i, 'net_debt_issuance'] = None


        transformed_df.at[i, 'common_stock_repurchased'] = data.get('Repurchase of Capital Stock', None)
        transformed_df.at[i, 'dividends_paid'] = data.get('Cash Dividends Paid', None)

        transformed_df.at[i, 'free_cash_flow'] = data.get('Free Cash Flow', None)
        transformed_df.at[i, 'end_cash_position'] = data.get('End Cash Position', None)
        transformed_df.at[i, 'net_change_in_cash'] = data.get('Changes in Cash', None)
        transformed_df.at[i, 'income_tax_paid'] = data.get('Income Tax Paid Supplemental Data', None)
        transformed_df.at[i, 'interest_paid'] = data.get('Interest Paid Supplemental Data', None)

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed cash flow statements data into the core.cash_flow_statements_quarterly table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.cash_flow_statements_quarterly schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.cash_flow_statements_quarterly
        total_records = insert_records(conn, transformed_df, 'core.cash_flow_statements_quarterly', ['tic', 'calendar_year', 'calendar_quarter'])
        print(f"Total records inserted/updated in core.cash_flow_statements_quarterly: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for cash flow statements.
    """
    # Step 1: Read raw cash flow statements
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.cash_flow_statements_quarterly
    load_records(transformed_df)

if __name__ == "__main__":
    main()