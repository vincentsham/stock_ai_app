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
    WHERE i.source = 'fmp'
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
        # Mapping: { Inner JSON Key : Core DB Column }
        third_source_mapping = {
            # --- Metadata (Inside raw_json) ---
            "symbol": "symbol",
            "period": "period",
            
            # --- 1. ASSETS ---
            "totalAssets": "total_assets",
            "totalCurrentAssets": "total_current_assets",
            
            # Cash & Liquidity
            "cashAndShortTermInvestments": "cash_and_short_term_investments",
            "cashAndCashEquivalents": "cash_and_cash_equivalents",
            
            # Receivables
            "netReceivables": "accounts_receivable",
            
            # Inventory (Total only)
            "inventory": "inventory",
            # GAP: Missing granular raw materials/finished goods
            
            # Long Term Assets
            "propertyPlantEquipmentNet": "net_ppe",
            "goodwillAndIntangibleAssets": "goodwill_and_intangibles",

            # --- 2. LIABILITIES ---
            "totalLiabilities": "total_liabilities",
            "totalCurrentLiabilities": "total_current_liabilities",
            
            # Operational Liabilities
            "accountPayables": "accounts_payable",
            "deferredRevenue": "deferred_revenue_current",
            "deferredRevenueNonCurrent": "deferred_revenue_non_current",
            
            # Debt
            "totalDebt": "total_debt",
            "longTermDebt": "long_term_debt",
            # GAP: 'current_debt_and_capital_lease' must be calculated
            
            # --- 3. EQUITY ---
            "totalStockholdersEquity": "total_equity",
            "retainedEarnings": "retained_earnings",
            "commonStock": "common_stock",
            
            # GAP: 'ordinary_shares_number' is missing
        }
        """

        # Assets
        transformed_df.at[i, "total_assets"] = data.get('totalAssets', None)
        transformed_df.at[i, "total_current_assets"] = data.get('totalCurrentAssets', None)
        transformed_df.at[i, "cash_and_short_term_investments"] = data.get('cashAndShortTermInvestments', None)
        transformed_df.at[i, "cash_and_cash_equivalents"] = data.get('cashAndCashEquivalents', None)

        transformed_df.at[i, "accounts_receivable"] = data.get('netReceivables', None)
        transformed_df.at[i, "inventory"] = data.get('inventory', None)

        transformed_df.at[i, "net_ppe"] = data.get('propertyPlantEquipmentNet', None)
        transformed_df.at[i, "goodwill_and_intangibles"] = data.get('goodwillAndIntangibleAssets', None)

        # Liabilities
        transformed_df.at[i, "total_liabilities"] = data.get('totalLiabilities', None)
        transformed_df.at[i, "total_current_liabilities"] = data.get('totalCurrentLiabilities', None)
        transformed_df.at[i, "accounts_payable"] = data.get('accountPayables', None)
        transformed_df.at[i, "deferred_revenue_current"] = data.get('deferredRevenue', None)
        transformed_df.at[i, "deferred_revenue_non_current"] = data.get('deferredRevenueNonCurrent', None)

        # Debt
        transformed_df.at[i, "total_debt"] = data.get('totalDebt', None)
        transformed_df.at[i, "long_term_debt"] = data.get('longTermDebt', None)
        # A. Current Debt + Lease
        # Logic: shortTermDebt + capitalLeaseObligationsCurrent
        st_debt = data.get("shortTermDebt", None)
        st_lease = data.get("capitalLeaseObligationsCurrent", None)
        if st_debt is not None or st_lease is not None:
            transformed_df.at[i, "current_debt_and_capital_lease"] = (st_debt or 0) + (st_lease or 0)
        else:
            transformed_df.at[i, "current_debt_and_capital_lease"] = None
        # Equity
        transformed_df.at[i, "total_equity"] = data.get('totalStockholdersEquity', None)
        transformed_df.at[i, "retained_earnings"] = data.get('retainedEarnings', None)
        transformed_df.at[i, "common_stock"] = data.get('commonStock', None)

        # B. Working Capital
        # Logic: Current Assets - Current Liabilities
        ca = data.get("totalCurrentAssets", None)
        cl = data.get("totalCurrentLiabilities", None)
        if ca is not None or cl is not None:
            transformed_df.at[i, "working_capital"] = (ca or 0) - (cl or 0)
        else:
            transformed_df.at[i, "working_capital"] = None
    
        # C. Net Tangible Assets
        # Logic: Equity - Goodwill/Intangibles
        eq = data.get("totalStockholdersEquity", None)
        intangibles = data.get("goodwillAndIntangibleAssets", None)
        if eq is not None or intangibles is not None:
            transformed_df.at[i, "net_tangible_assets"] = (eq or 0) - (intangibles or 0)
        else:
            transformed_df.at[i, "net_tangible_assets"] = None

        # D. Invested Capital
        # Logic: Equity + Total Debt
        total_debt = data.get("totalDebt", None)
        if eq is not None or total_debt is not None:
            transformed_df.at[i, "invested_capital"] = (eq or 0) + (total_debt or 0)
        else:
            transformed_df.at[i, "invested_capital"] = None
        
        # E. Ordinary Shares Number
        transformed_df.at[i, "ordinary_shares_number"] = None

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