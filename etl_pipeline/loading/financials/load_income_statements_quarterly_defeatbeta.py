import pandas as pd
import json
from database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.income_statements table and returns it as a pandas DataFrame.
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
    FROM raw.income_statements_quarterly as i
    INNER JOIN core.earnings_calendar as c
    ON i.tic = c.tic AND ABS(i.fiscal_date::DATE - c.fiscal_date::DATE) <= 15
    LEFT JOIN core.income_statements_quarterly AS ci
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
        transformed_df.at[i, 'calendar_year'] = raw_df.iloc[i]['calendar_year']
        transformed_df.at[i, 'calendar_quarter'] = raw_df.iloc[i]['calendar_quarter']
        transformed_df.at[i, 'earnings_date'] = raw_df.iloc[i]['earnings_date']
        transformed_df.at[i, 'fiscal_year'] = raw_df.iloc[i]['fiscal_year']
        transformed_df.at[i, 'fiscal_quarter'] = raw_df.iloc[i]['fiscal_quarter']
        transformed_df.at[i, 'fiscal_date'] = raw_df.iloc[i]['fiscal_date']
        
        """
        # Final Mapping: { Raw API Key : Core DB Column }
        column_mapping = {
            # --- 1. Top Line ---
            "Total Revenue": "revenue",
            "Cost of Revenue": "cost_of_revenue",
            "Gross Profit": "gross_profit",

            # --- 2. Expenses ---
            "Research & Development": "research_and_development",
            "Selling General and Administrative": "selling_general_admin",
            "Reconciled Depreciation": "depreciation_amortization",
            "Operating Expense": "operating_expenses",

            # --- 3. Operating Profitability ---
            "Operating Income": "operating_income",
            "EBITDA": "ebitda",
            "EBIT": "ebit",

            # --- 4. Non-Operating Items ---
            "Interest Income": "interest_income",
            "Interest Expense": "interest_expense",
            "Other Income Expense": "other_non_operating_income",

            # --- 5. Pre-Tax & Tax ---
            "Pretax Income": "income_before_tax",
            "Tax Provision": "income_tax_expense",
            "Tax Rate for Calcs": "effective_tax_rate",

            # --- 6. Bottom Line ---
            "Net Income Common Stockholders": "net_income",

            # --- 7. Share Information ---
            "Basic Average Shares": "weighted_average_shares_basic",
            "Diluted Average Shares": "weighted_average_shares_diluted",
            "Basic EPS": "eps",
            "Diluted EPS": "eps_diluted"
        }
        """

        transformed_df.at[i, 'revenue'] = data.get('Total Revenue', None)
        transformed_df.at[i, 'cost_of_revenue'] = data.get('Cost of Revenue', None)
        transformed_df.at[i, 'gross_profit'] = data.get('Gross Profit', None)

        transformed_df.at[i, 'research_and_development'] = data.get('Research & Development', None)
        transformed_df.at[i, 'selling_general_admin'] = data.get('Selling General and Administrative', None)
        transformed_df.at[i, 'depreciation_amortization'] = data.get('Reconciled Depreciation', None)
        transformed_df.at[i, 'operating_expenses'] = data.get('Operating Expense', None)

        transformed_df.at[i, 'operating_income'] = data.get('Operating Income', None)
        transformed_df.at[i, 'ebitda'] = data.get('EBITDA', None)
        transformed_df.at[i, 'ebit'] = data.get('EBIT', None)

        transformed_df.at[i, 'interest_income'] = data.get('Interest Income', None)
        transformed_df.at[i, 'interest_expense'] = data.get('Interest Expense', None)
        transformed_df.at[i, 'other_non_operating_income'] = data.get('Other Income Expense', None)

        transformed_df.at[i, 'income_before_tax'] = data.get('Pretax Income', None)
        transformed_df.at[i, 'income_tax_expense'] = data.get('Tax Provision', None)
        transformed_df.at[i, 'effective_tax_rate'] = data.get('Tax Rate for Calcs', None)
        transformed_df.at[i, 'effective_tax_rate'] = transformed_df.at[i, 'effective_tax_rate'].clip(0, 0.55) \
                                                    if transformed_df.at[i, 'effective_tax_rate'] is not None else None

        transformed_df.at[i, 'net_income'] = data.get('Net Income Common Stockholders', None)

        transformed_df.at[i, 'weighted_average_shares_basic'] = data.get('Basic Average Shares', None)
        transformed_df.at[i, 'weighted_average_shares_diluted'] = data.get('Diluted Average Shares', None)
        transformed_df.at[i, 'eps'] = data.get('Basic EPS', None)
        transformed_df.at[i, 'eps_diluted'] = data.get('Diluted EPS', None)

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']


    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.income_statements_quarterly table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.income_statements_quarterly schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.income_statements_quarterly
        total_records = insert_records(conn, transformed_df, 'core.income_statements_quarterly', ['tic', 'calendar_year', 'calendar_quarter'])
        print(f"Total records inserted/updated in core.income_statements_quarterly: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for income statements.
    """
    # Step 1: Read raw income statements
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.income_statements_quarterly
    load_records(transformed_df)

if __name__ == "__main__":
    main()