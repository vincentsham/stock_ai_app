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
    WHERE i.source = 'fmp'
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
        # Mapping: { Second Dict Key : Core DB Column }
        second_source_mapping = {
            # --- 1. Metadata ---
            "symbol": "symbol",
            "period": "period",
            "date": "date",

            # --- 2. Top Line ---
            "revenue": "revenue",
            "costOfRevenue": "cost_of_revenue",
            "grossProfit": "gross_profit",

            # --- 3. Expenses ---
            "researchAndDevelopmentExpenses": "research_and_development",
            "sellingGeneralAndAdministrativeExpenses": "selling_general_admin",
            "depreciationAndAmortization": "depreciation_amortization",
            "operatingExpenses": "operating_expenses",

            # --- 4. Operating Profitability ---
            "operatingIncome": "operating_income",
            "ebitda": "ebitda",
            "ebit": "ebit",

            # --- 5. Non-Operating Items ---
            "interestIncome": "interest_income",
            "interestExpense": "interest_expense",
            # Note: 'other_non_operating_income' is not explicitly separated 
            # in this source; it is aggregated into 'totalOtherIncomeExpensesNet'.

            # --- 6. Pre-Tax & Tax ---
            "incomeBeforeTax": "income_before_tax",
            "incomeTaxExpense": "income_tax_expense",

            # --- 7. Bottom Line ---
            "netIncome": "net_income",
            
            # --- 8. Share Information ---
            "weightedAverageShsOut": "weighted_average_shares_basic",
            "weightedAverageShsOutDil": "weighted_average_shares_diluted",
            "eps": "eps",
            "epsDiluted": "eps_diluted"
        }
        """


        transformed_df.at[i, 'revenue'] = data.get('revenue', None)
        transformed_df.at[i, 'cost_of_revenue'] = data.get('costOfRevenue', None)
        transformed_df.at[i, 'gross_profit'] = data.get('grossProfit', None)

        transformed_df.at[i, 'research_and_development'] = data.get('researchAndDevelopmentExpenses', None)
        transformed_df.at[i, 'selling_general_admin'] = data.get('sellingGeneralAndAdministrativeExpenses', None)
        transformed_df.at[i, 'depreciation_amortization'] = data.get('depreciationAndAmortization', None)
        transformed_df.at[i, 'operating_expenses'] = data.get('operatingExpenses', None)

        transformed_df.at[i, 'operating_income'] = data.get('operatingIncome', None)
        transformed_df.at[i, 'ebitda'] = data.get('ebitda', None)
        transformed_df.at[i, 'ebit'] = data.get('ebit', None)

        transformed_df.at[i, 'interest_income'] = data.get('interestIncome', None)
        transformed_df.at[i, 'interest_expense'] = data.get('interestExpense', None)

        transformed_df.at[i, 'income_before_tax'] = data.get('incomeBeforeTax', None)
        transformed_df.at[i, 'income_tax_expense'] = data.get('incomeTaxExpense', None)

        total_other_income = data.get('totalOtherIncomeExpensesNet', None)
        net_interest_income = data.get('netInterestIncome', None)
        if total_other_income is not None or net_interest_income is not None:
            other_non_operating_income = (total_other_income or 0) - (net_interest_income or 0)
        else:
            other_non_operating_income = None
        transformed_df.at[i, 'other_non_operating_income'] = other_non_operating_income

        transformed_df.at[i, 'net_income'] = data.get('netIncome', None)

        transformed_df.at[i, 'weighted_average_shares_basic'] = data.get('weightedAverageShsOut', None)
        transformed_df.at[i, 'weighted_average_shares_diluted'] = data.get('weightedAverageShsOutDil', None)
        transformed_df.at[i, 'eps'] = data.get('eps', None)
        transformed_df.at[i, 'eps_diluted'] = data.get('epsDiluted', None)


        transformed_df.at[i, 'effective_tax_rate'] = (
            data.get('incomeTaxExpense', None) / data.get('incomeBeforeTax', None)
            if data.get('incomeBeforeTax', None) not in (0, None)
            and data.get('incomeTaxExpense', None) is not None
            else None
        )
        transformed_df.at[i, 'effective_tax_rate'] = (
            transformed_df.at[i, 'effective_tax_rate'].clip(0, 0.55)
            if transformed_df.at[i, 'effective_tax_rate'] is not None else None
        )


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