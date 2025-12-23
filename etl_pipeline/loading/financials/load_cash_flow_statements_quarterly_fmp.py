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
    WHERE i.source = 'fmp'
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
        # Mapping: { Inner JSON Key : Core DB Column }
        second_cash_flow_mapping = {
            # --- Metadata ---
            "symbol": "symbol",
            "period": "period",
            # Use top-level 'fiscal_date' or inner 'date'
            
            # --- 1. Operating Activities ---
            "netIncome": "net_income",
            "operatingCashFlow": "operating_cash_flow",
            "depreciationAndAmortization": "depreciation_amortization",
            "deferredIncomeTax": "deferred_income_tax",
            "stockBasedCompensation": "stock_based_compensation",
            
            # Working Capital Changes
            # In CF statements, these keys represent the *flow* (Change), not the Balance.
            "changeInWorkingCapital": "change_in_working_capital",
            "accountsReceivables": "change_in_receivables",
            "inventory": "change_in_inventory",
            "accountsPayables": "change_in_accounts_payable",

            # --- 2. Investing Activities ---
            "netCashProvidedByInvestingActivities": "investing_cash_flow",
            "capitalExpenditure": "capital_expenditure",
            "acquisitionsNet": "acquisitions_net",
            "purchasesOfInvestments": "investments_purchases",
            "salesMaturitiesOfInvestments": "investments_sales",

            # --- 3. Financing Activities ---
            "netCashProvidedByFinancingActivities": "financing_cash_flow",
            "commonStockRepurchased": "common_stock_repurchased",
            "commonDividendsPaid": "dividends_paid",
            
            # Debt Logic: This source often gives 'Net' debt. 
            # We will need custom logic to map this to issuance/repayment if distinct keys represent them.
            # In this specific dict, 'netDebtIssuance' is 0.

            # --- 4. Summary & Supplemental ---
            "freeCashFlow": "free_cash_flow",
            "cashAtEndOfPeriod": "end_cash_position",
            "netChangeInCash": "net_change_in_cash",
            "incomeTaxesPaid": "income_tax_paid",
            "interestPaid": "interest_paid"
        }
        
        """

        transformed_df.at[i, 'net_income'] = data.get('netIncome', None)
        transformed_df.at[i, 'operating_cash_flow'] = data.get('operatingCashFlow', None)
        transformed_df.at[i, 'depreciation_amortization'] = data.get('depreciationAndAmortization', None)
        transformed_df.at[i, 'deferred_income_tax'] = data.get('deferredIncomeTax', None)
        transformed_df.at[i, 'stock_based_compensation'] = data.get('stockBasedCompensation', None)

        transformed_df.at[i, 'change_in_working_capital'] = data.get('changeInWorkingCapital', None)
        transformed_df.at[i, 'change_in_receivables'] = data.get('accountsReceivables', None)
        transformed_df.at[i, 'change_in_inventory'] = data.get('inventory', None)
        transformed_df.at[i, 'change_in_accounts_payable'] = data.get('accountsPayables', None)

        transformed_df.at[i, 'investing_cash_flow'] = data.get('netCashProvidedByInvestingActivities', None)
        transformed_df.at[i, 'capital_expenditure'] = data.get('capitalExpenditure', None)
        transformed_df.at[i, 'acquisitions_net'] = data.get('acquisitionsNet', None)
        transformed_df.at[i, 'investments_purchases'] = data.get('purchasesOfInvestments', None)
        transformed_df.at[i, 'investments_sales'] = data.get('salesMaturitiesOfInvestments', None)

        transformed_df.at[i, 'financing_cash_flow'] = data.get('netCashProvidedByFinancingActivities', None)
        transformed_df.at[i, 'net_debt_issuance'] = data.get('netDebtIssuance', None)
        transformed_df.at[i, 'common_stock_repurchased'] = data.get('commonStockRepurchased', None)
        transformed_df.at[i, 'dividends_paid'] = data.get('commonDividendsPaid', None) or data.get('netDividendsPaid', None)

        transformed_df.at[i, 'free_cash_flow'] = data.get('freeCashFlow', None)
        transformed_df.at[i, 'end_cash_position'] = data.get('cashAtEndOfPeriod', None)
        transformed_df.at[i, 'net_change_in_cash'] = data.get('netChangeInCash', None)
        transformed_df.at[i, 'income_tax_paid'] = data.get('incomeTaxesPaid', None)
        transformed_df.at[i, 'interest_paid'] = data.get('interestPaid', None)

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    transformed_df = transformed_df[transformed_df['fiscal_quarter'] != 0]
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