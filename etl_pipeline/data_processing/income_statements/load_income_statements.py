import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query


def read_income_statements():
    """
    Reads data from the raw.income_statements table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT 
        tic, 
        fiscal_year, 
        fiscal_quarter, 
        source, 
        raw_json, 
        raw_json_sha256, 
        updated_at
    FROM raw.income_statements;
    """

    # Connect to the database
    df = execute_query(query)
    return df


def transform_income_statements(raw_df):
    """
    Transforms the raw income statements data to match the schema of core.income_statements.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw income statements data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.income_statements schema.
    """
    transformed_df = pd.DataFrame()

    # Map columns from raw to core schema
    for i in range(len(raw_df)):

        data = raw_df.iloc[i]['raw_json']

        transformed_df.at[i, 'tic'] = raw_df.iloc[i]['tic']
        transformed_df.at[i, 'fiscal_year'] = raw_df.iloc[i]['fiscal_year']
        transformed_df.at[i, 'fiscal_quarter'] = raw_df.iloc[i]['fiscal_quarter']
        transformed_df.at[i, 'period'] = data.get('period', None)
        transformed_df.at[i, 'earnings_date'] = data.get('date', None)
        transformed_df.at[i, 'filing_date'] = data.get('filingDate', None)
        transformed_df.at[i, 'accepted_date'] = data.get('acceptedDate', None)
        transformed_df.at[i, 'cik'] = data.get('cik', None)
        transformed_df.at[i, 'reported_currency'] = data.get('reportedCurrency', None)
        
        transformed_df.at[i, 'revenue'] = data.get('revenue', None)
        transformed_df.at[i, 'cost_of_revenue'] = data.get('costOfRevenue', None)
        transformed_df.at[i, 'gross_profit'] = data.get('grossProfit', None)
        transformed_df.at[i, 'research_and_development_expenses'] = data.get('researchAndDevelopmentExpenses', None)
        transformed_df.at[i, 'general_and_administrative_expenses'] = data.get('generalAndAdministrativeExpenses', None)
        transformed_df.at[i, 'selling_and_marketing_expenses'] = data.get('sellingAndMarketingExpenses', None)
        transformed_df.at[i, 'selling_general_and_administrative_expenses'] = data.get('sellingGeneralAndAdministrativeExpenses', None)
        transformed_df.at[i, 'other_expenses'] = data.get('otherExpenses', None)
        transformed_df.at[i, 'operating_expenses'] = data.get('operatingExpenses', None)
        transformed_df.at[i, 'cost_and_expenses'] = data.get('costAndExpenses', None)
        
        transformed_df.at[i, 'ebitda'] = data.get('ebitda', None)
        transformed_df.at[i, 'ebit'] = data.get('ebit', None)
        transformed_df.at[i, 'non_operating_income_excluding_interest'] = data.get('nonOperatingIncomeExcludingInterest', None)
        transformed_df.at[i, 'operating_income'] = data.get('operatingIncome', None)
        transformed_df.at[i, 'total_other_income_expenses_net'] = data.get('totalOtherIncomeExpensesNet', None)
        transformed_df.at[i, 'income_before_tax'] = data.get('incomeBeforeTax', None)
        transformed_df.at[i, 'income_tax_expense'] = data.get('incomeTaxExpense', None)
        
        transformed_df.at[i, 'net_income_from_continuing_operations'] = data.get('netIncomeFromContinuingOperations', None)
        transformed_df.at[i, 'net_income_from_discontinued_operations'] = data.get('netIncomeFromDiscontinuedOperations', None)
        transformed_df.at[i, 'other_adjustments_to_net_income'] = data.get('otherAdjustmentsToNetIncome', None)
        transformed_df.at[i, 'net_income'] = data.get('netIncome', None)
        transformed_df.at[i, 'net_income_deductions'] = data.get('netIncomeDeductions', None)
        transformed_df.at[i, 'bottom_line_net_income'] = data.get('bottomLineNetIncome', None)
        
        transformed_df.at[i, 'net_interest_income'] = data.get('netInterestIncome', None)
        transformed_df.at[i, 'interest_income'] = data.get('interestIncome', None)
        transformed_df.at[i, 'interest_expense'] = data.get('interestExpense', None)
        transformed_df.at[i, 'depreciation_and_amortization'] = data.get('depreciationAndAmortization', None)

        transformed_df.at[i, 'eps'] = data.get('eps', None)
        transformed_df.at[i, 'eps_diluted'] = data.get('epsDiluted', None)
        transformed_df.at[i, 'weighted_average_shs_out'] = data.get('weightedAverageShsOut', None)
        transformed_df.at[i, 'weighted_average_shs_out_dil'] = data.get('weightedAverageShsOutDil', None)


        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']


    return transformed_df


def load_income_statements(transformed_df):
    """
    Loads the transformed income statements data into the core.income_statements table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.income_statements schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.income_statements
        total_records = insert_records(conn, transformed_df, 'core.income_statements', ['tic', 'fiscal_year', 'fiscal_quarter'])
        print(f"Total records inserted/updated in core.income_statements: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for income statements.
    """
    # Step 1: Read raw income statements
    raw_df = read_income_statements()

    # Step 2: Transform the data
    transformed_df = transform_income_statements(raw_df)

    # Step 3: Load the transformed data into core.income_statements
    load_income_statements(transformed_df)

if __name__ == "__main__":
    main()