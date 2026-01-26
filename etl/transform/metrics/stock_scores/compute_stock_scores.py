from database.utils import connect_to_db, execute_query, insert_records, read_sql_query
import pandas as pd
import yfinance as yf
import numpy as np


def _to_float_or_nan(value) -> float:
    if value is None:
        return float("nan")
    if pd.isna(value):
        return float("nan")
    try:
        return float(value)
    except Exception:
        return float("nan")


def _nanmin(values) -> float:
    arr = np.array([_to_float_or_nan(v) for v in values], dtype=float)
    if arr.size == 0 or np.isnan(arr).all():
        return float("nan")
    return float(np.nanmin(arr))


def _nanmax(values) -> float:
    arr = np.array([_to_float_or_nan(v) for v in values], dtype=float)
    if arr.size == 0 or np.isnan(arr).all():
        return float("nan")
    return float(np.nanmax(arr))

def _nanmean(values) -> float:
    arr = np.array([_to_float_or_nan(v) for v in values], dtype=float)
    if arr.size == 0 or np.isnan(arr).all():
        return float("nan")
    return float(np.nanmean(arr))


def compute_valuation_score(row):
    cols = []
    cols.append(100 - _to_float_or_nan(row['pe_ttm_percentile']))
    cols.append(100 - _to_float_or_nan(row['pe_forward_percentile']))
    cols.append(100 - _to_float_or_nan(row['peg_ratio_forward_percentile']))
    cols.append(100 - _to_float_or_nan(row['p_to_fcf_ttm_percentile']))

    max_score = _nanmax(cols)
    min_score = _nanmin(cols)
    return 0.75 * max_score + 0.25 * min_score

def compute_profitability_score(row):
    cols = [
        row['net_margin_percentile'],
        row['roe_percentile'],
        row['fcf_margin_percentile'],
        row['roic_percentile'],
    ]
    max_score = _nanmax(cols)
    min_score = _nanmin(cols)
    return 0.75 * max_score + 0.25 * min_score

def compute_growth_score(row):
    cols = [
        row['forward_revenue_growth_percentile'],
        row['revenue_growth_yoy_percentile'],
        row['revenue_cagr_3y_percentile'],
    ]
    if pd.notna(row.get('ebitda_growth_yoy_percentile')):
        cols.append(row['ebitda_growth_yoy_percentile'])
    if pd.notna(row.get('forward_eps_growth_percentile')):
        cols.append(row['forward_eps_growth_percentile'])
    elif pd.notna(row.get('eps_growth_yoy_percentile')):
        cols.append(row['eps_growth_yoy_percentile'])

    max_score = _nanmax(cols)
    min_score = _nanmin(cols)
    return 0.75 * max_score + 0.25 * min_score

def compute_efficiency_score(row):
    cols = [
        row['asset_turnover_percentile'],
        row['fixed_asset_turnover_percentile']
    ]
    cols_inventory = []
    cols_inventory.append(100 - _to_float_or_nan(row['dio_percentile']))
    cols_inventory.append(100 - _to_float_or_nan(row['dpo_percentile']))
    cols_inventory.append(100 - _to_float_or_nan(row['dso_percentile']))
    cols_inventory.append(100 - _to_float_or_nan(row['cash_conversion_cycle_percentile']))

    cols_non_inventory = []
    cols_non_inventory.append(row['revenue_per_employee_percentile'])
    cols_non_inventory.append(100 - _to_float_or_nan(row['opex_ratio_percentile']))

    if _nanmean(cols_inventory) != float("nan") and _nanmean(cols_inventory) > _nanmean(cols_non_inventory):
        cols += cols_inventory
    elif _nanmean(cols_non_inventory) != float("nan"):
        cols += cols_non_inventory

    max_score = _nanmax(cols)
    min_score = _nanmin(cols)
    return 0.75 * max_score + 0.25 * min_score

def compute_financial_health_score(row):
    cols = [row['interest_coverage_ttm_percentile']]
    cols.append(
        _nanmax(
            [
                100 - _to_float_or_nan(row['net_debt_to_ebitda_ttm_percentile']),
                100 - _to_float_or_nan(row['debt_to_assets_percentile']),
                100 - _to_float_or_nan(row['debt_to_equity_percentile']),
                row['altman_z_score_percentile']

            ]
        )
    )
    cols.append(_nanmax([row['current_ratio_percentile'], row['cash_ratio_percentile']]))

    max_score = _nanmax(cols)
    min_score = _nanmin(cols)
    return 0.75 * max_score + 0.25 * min_score

    

    

def transform_records(conn, tic: str) -> pd.DataFrame:
    percentiles_query = f"""
        SELECT vp.tic, vp.date::date,
               vp.pe_ttm_percentile, vp.pe_forward_percentile, vp.peg_ratio_forward_percentile, vp.p_to_fcf_ttm_percentile,
               pp.net_margin_percentile, pp.roe_percentile, pp.roic_percentile, pp.fcf_margin_percentile,
               gp.forward_revenue_growth_percentile, gp.revenue_growth_yoy_percentile, gp.revenue_cagr_3y_percentile, gp.ebitda_growth_yoy_percentile, gp.forward_eps_growth_percentile, gp.eps_growth_yoy_percentile,
               ep.asset_turnover_percentile, ep.dio_percentile, ep.dpo_percentile, ep.dso_percentile, ep.cash_conversion_cycle_percentile, ep.opex_ratio_percentile, ep.revenue_per_employee_percentile, ep.fixed_asset_turnover_percentile,
               fhp.interest_coverage_ttm_percentile, fhp.net_debt_to_ebitda_ttm_percentile, fhp.debt_to_assets_percentile, fhp.debt_to_equity_percentile, fhp.altman_z_score_percentile, fhp.current_ratio_percentile, fhp.cash_ratio_percentile
        FROM core.valuation_percentiles vp
        JOIN core.profitability_percentiles pp ON vp.tic = pp.tic AND vp.date = pp.date
        JOIN core.growth_percentiles gp ON vp.tic = gp.tic AND vp.date = gp.date
        JOIN core.efficiency_percentiles ep ON vp.tic = ep.tic AND vp.date = ep.date
        JOIN core.financial_health_percentiles fhp ON vp.tic = fhp.tic AND vp.date = fhp.date
        WHERE vp.tic = '{tic}'
        ORDER BY vp.date;
    """
    df = read_sql_query(percentiles_query, conn)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['valuation_score'] = df.apply(compute_valuation_score, axis=1)
    df['profitability_score'] = df.apply(compute_profitability_score, axis=1)
    df['growth_score'] = df.apply(compute_growth_score, axis=1)
    df['efficiency_score'] = df.apply(compute_efficiency_score, axis=1)
    df['financial_health_score'] = df.apply(compute_financial_health_score, axis=1)
    df['total_score'] = (df['valuation_score'] + df['profitability_score'] +
                         0.8 * df['growth_score'] + 0.25 * df['efficiency_score'] + 0.25 * df['financial_health_score']) / 3.3

    df[['valuation_score', 'profitability_score', 'growth_score',
        'efficiency_score', 'financial_health_score', 'total_score']] = df[['valuation_score', 'profitability_score', 'growth_score',
                                                                          'efficiency_score', 'financial_health_score', 'total_score']].ffill()
 
    transformed_df = df[['tic', 'date', 'valuation_score', 'profitability_score',
                         'growth_score', 'efficiency_score', 'financial_health_score', 'total_score']]
    return transformed_df

    


def load_records(transformed_df, conn):
    total_records = insert_records(conn, transformed_df, 'core.stock_scores', ['tic', 'date'])
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
            transformed_df = transform_records(conn, tic)
            if transformed_df.empty:
                print("No new or updated records to process.")
                continue
  
            total_records = load_records(transformed_df, conn)
            print(f"Total records inserted/updated for {tic}: {total_records}")

    return


if __name__ == "__main__":
    main()

