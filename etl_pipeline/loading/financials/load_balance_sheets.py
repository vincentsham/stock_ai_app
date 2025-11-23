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
        i.fiscal_year, 
        i.fiscal_quarter, 
        i.fiscal_date,
        i.source, 
        i.raw_json, 
        i.raw_json_sha256 
    FROM raw.balance_sheets as i
    INNER JOIN core.earnings_calendar as c
    ON i.tic = c.tic AND ABS(i.fiscal_date::DATE - c.fiscal_date::DATE) <= 15
    LEFT JOIN core.balance_sheets AS ci
    ON i.tic = ci.tic AND i.fiscal_year = ci.fiscal_year AND i.fiscal_quarter = ci.fiscal_quarter
    WHERE ci.raw_json_sha256 IS NULL 
        OR i.raw_json_sha256 IS DISTINCT FROM ci.raw_json_sha256;
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
        transformed_df.at[i, 'period'] = data.get('period', None)
        transformed_df.at[i, 'filing_date'] = data.get('filingDate', None)
        transformed_df.at[i, 'accepted_date'] = data.get('acceptedDate', None)
        transformed_df.at[i, 'cik'] = data.get('cik', None)
        transformed_df.at[i, 'reported_currency'] = data.get('reportedCurrency', None)

        """
            -- Assets
            cash_and_cash_equivalents           BIGINT,
            short_term_investments              BIGINT,
            cash_and_short_term_investments     BIGINT,
            net_receivables                     BIGINT,
            accounts_receivables                BIGINT,
            other_receivables                   BIGINT,
            inventory                           BIGINT,
            prepaids                            BIGINT,
            other_current_assets                BIGINT,
            total_current_assets                BIGINT,

            property_plant_equipment_net        BIGINT,
            goodwill                            BIGINT,
            intangible_assets                   BIGINT,
            goodwill_and_intangible_assets      BIGINT,
            long_term_investments               BIGINT,
            tax_assets                          BIGINT,
            other_non_current_assets            BIGINT,
            total_non_current_assets            BIGINT,
            other_assets                        BIGINT,
            total_assets                        BIGINT,

            -- Liabilities
            total_payables                      BIGINT,
            account_payables                    BIGINT,
            other_payables                      BIGINT,
            accrued_expenses                    BIGINT,
            short_term_debt                     BIGINT,
            capital_lease_obligations_current   BIGINT,
            tax_payables                        BIGINT,
            deferred_revenue                    BIGINT,
            other_current_liabilities           BIGINT,
            total_current_liabilities           BIGINT,

            long_term_debt                      BIGINT,
            capital_lease_obligations_non_current   BIGINT,
            deferred_revenue_non_current        BIGINT,
            deferred_tax_liabilities_non_current BIGINT,
            other_non_current_liabilities       BIGINT,
            total_non_current_liabilities       BIGINT,

            other_liabilities                   BIGINT,
            capital_lease_obligations           BIGINT,
            total_liabilities                   BIGINT,

            -- Equity
            treasury_stock                      BIGINT,
            preferred_stock                     BIGINT,
            common_stock                        BIGINT,
            retained_earnings                   BIGINT,
            additional_paid_in_capital          BIGINT,
            accumulated_other_comprehensive_income_loss BIGINT,
            other_total_stockholders_equity     BIGINT,
            total_stockholders_equity           BIGINT,
            total_equity                        BIGINT,
            minority_interest                   BIGINT,
            total_liabilities_and_total_equity  BIGINT,

            -- Derived Totals
            total_investments                   BIGINT,
            total_debt                          BIGINT,
            net_debt                            BIGINT,
        """

        # Assets
        transformed_df.at[i, 'cash_and_cash_equivalents'] = data.get('cashAndCashEquivalents', None)
        transformed_df.at[i, 'short_term_investments'] = data.get('shortTermInvestments', None)
        transformed_df.at[i, 'cash_and_short_term_investments'] = data.get('cashAndShortTermInvestments', None)
        transformed_df.at[i, 'net_receivables'] = data.get('netReceivables', None)
        transformed_df.at[i, 'accounts_receivables'] = data.get('accountsReceivables', None)
        transformed_df.at[i, 'other_receivables'] = data.get('otherReceivables', None)
        transformed_df.at[i, 'inventory'] = data.get('inventory', None)
        transformed_df.at[i, 'prepaids'] = data.get('prepaids', None)
        transformed_df.at[i, 'other_current_assets'] = data.get('otherCurrentAssets', None)
        transformed_df.at[i, 'total_current_assets'] = data.get('totalCurrentAssets', None)

        transformed_df.at[i, 'property_plant_equipment_net'] = data.get('propertyPlantEquipmentNet', None)
        transformed_df.at[i, 'goodwill'] = data.get('goodwill', None)
        transformed_df.at[i, 'intangible_assets'] = data.get('intangibleAssets', None)
        transformed_df.at[i, 'goodwill_and_intangible_assets'] = data.get('goodwillAndIntangibleAssets', None)
        transformed_df.at[i, 'long_term_investments'] = data.get('longTermInvestments', None)   
        transformed_df.at[i, 'tax_assets'] = data.get('taxAssets', None)
        transformed_df.at[i, 'other_non_current_assets'] = data.get('otherNonCurrentAssets', None)
        transformed_df.at[i, 'total_non_current_assets'] = data.get('totalNonCurrentAssets', None)
        transformed_df.at[i, 'other_assets'] = data.get('otherAssets', None)
        transformed_df.at[i, 'total_assets'] = data.get('totalAssets', None)

        # Liabilities
        transformed_df.at[i, 'total_payables'] = data.get('totalPayables', None)
        transformed_df.at[i, 'account_payables'] = data.get('accountPayables', None)
        transformed_df.at[i, 'other_payables'] = data.get('otherPayables', None)
        transformed_df.at[i, 'accrued_expenses'] = data.get('accruedExpenses', None)
        transformed_df.at[i, 'short_term_debt'] = data.get('shortTermDebt', None)
        transformed_df.at[i, 'capital_lease_obligations_current'] = data.get('capitalLeaseObligationsCurrent', None)        
        transformed_df.at[i, 'tax_payables'] = data.get('taxPayables', None)
        transformed_df.at[i, 'deferred_revenue'] = data.get('deferredRevenue', None)
        transformed_df.at[i, 'other_current_liabilities'] = data.get('otherCurrentLiabilities', None)
        transformed_df.at[i, 'total_current_liabilities'] = data.get('totalCurrentLiabilities', None)

        transformed_df.at[i, 'long_term_debt'] = data.get('longTermDebt', None)
        transformed_df.at[i, 'capital_lease_obligations_non_current'] = data.get('capitalLeaseObligationsNonCurrent', None)
        transformed_df.at[i, 'deferred_revenue_non_current'] = data.get('deferredRevenueNonCurrent', None)
        transformed_df.at[i, 'deferred_tax_liabilities_non_current'] = data.get('deferredTaxLiabilitiesNonCurrent', None)
        transformed_df.at[i, 'other_non_current_liabilities'] = data.get('otherNonCurrentLiabilities', None)
        transformed_df.at[i, 'total_non_current_liabilities'] = data.get('totalNonCurrentLiabilities', None)

        transformed_df.at[i, 'other_liabilities'] = data.get('otherLiabilities', None)
        transformed_df.at[i, 'capital_lease_obligations'] = data.get('capitalLeaseObligations', None)
        transformed_df.at[i, 'total_liabilities'] = data.get('totalLiabilities', None)

        # Equity
        transformed_df.at[i, 'treasury_stock'] = data.get('treasuryStock', None)
        transformed_df.at[i, 'preferred_stock'] = data.get('preferredStock', None)
        transformed_df.at[i, 'common_stock'] = data.get('commonStock', None)
        transformed_df.at[i, 'retained_earnings'] = data.get('retainedEarnings', None)
        transformed_df.at[i, 'additional_paid_in_capital'] = data.get('additionalPaidInCapital', None)
        transformed_df.at[i, 'accumulated_other_comprehensive_income_loss'] = data.get('accumulatedOtherComprehensiveIncomeLoss', None)
        transformed_df.at[i, 'other_total_stockholders_equity'] = data.get('otherTotalStockholdersEquity', None)
        transformed_df.at[i, 'total_stockholders_equity'] = data.get('totalStockholdersEquity', None)
        transformed_df.at[i, 'total_equity'] = data.get('totalEquity', None)
        transformed_df.at[i, 'minority_interest'] = data.get('minorityInterest', None)
        transformed_df.at[i, 'total_liabilities_and_total_equity'] = data.get('totalLiabilitiesAndTotalEquity', None)

        # Derived Totals
        transformed_df.at[i, 'total_investments'] = data.get('totalInvestments', None)
        transformed_df.at[i, 'total_debt'] = data.get('totalDebt', None)
        transformed_df.at[i, 'net_debt'] = data.get('netDebt', None)

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    transformed_df = transformed_df[transformed_df['fiscal_quarter'] != 0]
    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.balance_sheets table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.balance_sheets schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.balance_sheets
        total_records = insert_records(conn, transformed_df, 'core.balance_sheets', ['tic', 'fiscal_year', 'fiscal_quarter'])
        print(f"Total records inserted/updated in core.balance_sheets: {total_records}")


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