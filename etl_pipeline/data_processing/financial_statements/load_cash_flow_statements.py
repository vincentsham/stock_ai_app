import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query


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
        i.fiscal_year, 
        i.fiscal_quarter, 
        i.fiscal_date,
        i.source, 
        i.raw_json, 
        i.raw_json_sha256 
    FROM raw.cash_flow_statements as i
    LEFT JOIN core.earnings_calendar as c
    ON i.tic = c.tic AND ABS(i.fiscal_date::DATE - c.fiscal_date::DATE) <= 15
    LEFT JOIN core.cash_flow_statements AS ci
    ON i.tic = ci.tic AND i.fiscal_year = ci.fiscal_year AND i.fiscal_quarter = ci.fiscal_quarter
    WHERE ci.raw_json_sha256 IS NULL 
        OR i.raw_json_sha256 IS DISTINCT FROM ci.raw_json_sha256;
    """

    # Connect to the database
    df = execute_query(query)

    return df


def transform_records(raw_df):
    """
    Transforms the raw cash flow statements data to match the schema of core.cash_flow_statements.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw cash flow statements data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.cash_flow_statements schema.
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
        transformed_df.at[i, 'period'] = data.get('period', None)
        
        transformed_df.at[i, 'filing_date'] = data.get('filingDate', None)
        transformed_df.at[i, 'accepted_date'] = data.get('acceptedDate', None)
        transformed_df.at[i, 'cik'] = data.get('cik', None)
        transformed_df.at[i, 'reported_currency'] = data.get('reportedCurrency', None)
     
        """
            -- Operating Activities
            net_income                              BIGINT,
            depreciation_and_amortization           BIGINT,
            deferred_income_tax                     BIGINT,
            stock_based_compensation                BIGINT,
            change_in_working_capital               BIGINT,
            accounts_receivables                    BIGINT,
            inventory                               BIGINT,
            accounts_payables                       BIGINT,
            other_working_capital                   BIGINT,
            other_non_cash_items                    BIGINT,
            net_cash_provided_by_operating_activities BIGINT,

            -- Investing Activities
            investments_in_property_plant_and_equipment  BIGINT,
            acquisitions_net                         BIGINT,
            purchases_of_investments                 BIGINT,
            sales_maturities_of_investments          BIGINT,
            other_investing_activities               BIGINT,
            net_cash_provided_by_investing_activities BIGINT,

            -- Financing Activities
            net_debt_issuance                        BIGINT,
            long_term_net_debt_issuance              BIGINT,
            short_term_net_debt_issuance             BIGINT,
            net_stock_issuance                       BIGINT,
            net_common_stock_issuance                BIGINT,
            common_stock_issuance                    BIGINT,
            common_stock_repurchased                 BIGINT,
            net_preferred_stock_issuance             BIGINT,
            net_dividends_paid                       BIGINT,
            common_dividends_paid                    BIGINT,
            preferred_dividends_paid                 BIGINT,
            other_financing_activities               BIGINT,
            net_cash_provided_by_financing_activities BIGINT,

            -- Cash & Reconciliation
            effect_of_forex_changes_on_cash          BIGINT,
            net_change_in_cash                       BIGINT,
            cash_at_end_of_period                    BIGINT,
            cash_at_beginning_of_period              BIGINT,

            -- Derived / Analytical Metrics
            operating_cash_flow                      BIGINT,
            capital_expenditure                      BIGINT,
            free_cash_flow                           BIGINT,
            income_taxes_paid                        BIGINT,
            interest_paid                            BIGINT,
        """

        # -- Operating Activities
        transformed_df.at[i, 'net_income'] = data.get('netIncome', None)
        transformed_df.at[i, 'depreciation_and_amortization'] = data.get('depreciationAndAmortization', None)
        transformed_df.at[i, 'deferred_income_tax'] = data.get('deferredIncomeTax', None)
        transformed_df.at[i, 'stock_based_compensation'] = data.get('stockBasedCompensation', None)
        transformed_df.at[i, 'change_in_working_capital'] = data.get('changeInWorkingCapital', None)
        transformed_df.at[i, 'accounts_receivables'] = data.get('accountsReceivables', None)
        transformed_df.at[i, 'inventory'] = data.get('inventory', None)
        transformed_df.at[i, 'accounts_payables'] = data.get('accountsPayables', None)
        transformed_df.at[i, 'other_working_capital'] = data.get('otherWorkingCapital', None)
        transformed_df.at[i, 'other_non_cash_items'] = data.get('otherNonCashItems', None)
        transformed_df.at[i, 'net_cash_provided_by_operating_activities'] = data.get('netCashProvidedByOperatingActivities', None)

        # -- Investing Activities
        transformed_df.at[i, 'investments_in_property_plant_and_equipment'] = data.get('investmentsInPropertyPlantAndEquipment', None)
        transformed_df.at[i, 'acquisitions_net'] = data.get('acquisitionsNet', None)
        transformed_df.at[i, 'purchases_of_investments'] = data.get('purchasesOfInvestments', None)
        transformed_df.at[i, 'sales_maturities_of_investments'] = data.get('salesMaturitiesOfInvestments', None)
        transformed_df.at[i, 'other_investing_activities'] = data.get('otherInvestingActivities', None)
        transformed_df.at[i, 'net_cash_provided_by_investing_activities'] = data.get('netCashProvidedByInvestingActivities', None)

        # -- Financing Activities
        transformed_df.at[i, 'net_debt_issuance'] = data.get('netDebtIssuance', None)
        transformed_df.at[i, 'long_term_net_debt_issuance'] = data.get('longTermNetDebtIssuance', None)
        transformed_df.at[i, 'short_term_net_debt_issuance'] = data.get('shortTermNetDebtIssuance', None)
        transformed_df.at[i, 'net_stock_issuance'] = data.get('netStockIssuance', None)
        transformed_df.at[i, 'net_common_stock_issuance'] = data.get('netCommonStockIssuance', None)
        transformed_df.at[i, 'common_stock_issuance'] = data.get('commonStockIssuance', None)
        transformed_df.at[i, 'common_stock_repurchased'] = data.get('commonStockRepurchased', None)
        transformed_df.at[i, 'net_preferred_stock_issuance'] = data.get('netPreferredStockIssuance', None)
        transformed_df.at[i, 'net_dividends_paid'] = data.get('netDividendsPaid', None)
        transformed_df.at[i, 'common_dividends_paid'] = data.get('commonDividendsPaid', None)
        transformed_df.at[i, 'preferred_dividends_paid'] = data.get('preferredDividendsPaid', None)
        transformed_df.at[i, 'other_financing_activities'] = data.get('otherFinancingActivities', None)
        transformed_df.at[i, 'net_cash_provided_by_financing_activities'] = data.get('netCashProvidedByFinancingActivities', None)  

        # -- Cash & Reconciliation
        transformed_df.at[i, 'effect_of_forex_changes_on_cash'] = data.get('effectOfForexChangesOnCash', None)
        transformed_df.at[i, 'net_change_in_cash'] = data.get('netChangeInCash', None)
        transformed_df.at[i, 'cash_at_end_of_period'] = data.get('cashAtEndOfPeriod', None)     
        transformed_df.at[i, 'cash_at_beginning_of_period'] = data.get('cashAtBeginningOfPeriod', None)

        # -- Derived / Analytical Metrics
        transformed_df.at[i, 'operating_cash_flow'] = data.get('operatingCashFlow', None)
        transformed_df.at[i, 'capital_expenditure'] = data.get('capitalExpenditure', None)
        transformed_df.at[i, 'free_cash_flow'] = data.get('freeCashFlow', None)
        transformed_df.at[i, 'income_taxes_paid'] = data.get('incomeTaxesPaid', None)
        transformed_df.at[i, 'interest_paid'] = data.get('interestPaid', None)

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    transformed_df = transformed_df[transformed_df['fiscal_quarter'] != 0]
    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed cash flow statements data into the core.cash_flow_statements table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.cash_flow_statements schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.cash_flow_statements
        total_records = insert_records(conn, transformed_df, 'core.cash_flow_statements', ['tic', 'fiscal_year', 'fiscal_quarter'])
        print(f"Total records inserted/updated in core.cash_flow_statements: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for cash flow statements.
    """
    # Step 1: Read raw cash flow statements
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.cash_flow_statements
    load_records(transformed_df)

if __name__ == "__main__":
    main()