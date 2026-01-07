import requests
from etl.utils import hash_dict, hash_text, get_calendar_year_quarter, filter_complete_years
from database.utils import connect_to_db
import os
import pandas as pd
import json
from defeatbeta_api.data.ticker import Ticker



# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL_FMP = "https://financialmodelingprep.com/stable/earnings"
BASE_URL_COINCODEX = "https://coincodex.com/api/v1/stocks/get_historical/earnings"

# Fetch historical earnings data
def fetch_records_fmp(tic):
    url = f"{BASE_URL_FMP}?symbol={tic}"
    response = requests.get(url + f"&apikey={API_KEY}")
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data from {url} for {tic}: {response.status_code}")
        return [], None

def process_records_fmp(raw_json, tic):
    df = pd.DataFrame(raw_json)
    df['tic'] = tic
    df["date"] = pd.to_datetime(df["date"])
    df["fiscal_date"] = None
    df["session"] = None
    df['source'] = "fmp"
    df.loc[:, 'raw_json'] = [json.dumps(row) for row in raw_json]
    df.loc[:, 'raw_json_sha256'] = [hash_dict(row) for row in raw_json]
    df = df[df["epsActual"].notnull() | df["revenueActual"].notnull() | df["epsEstimated"].notnull() | df["revenueEstimated"].notnull()]
    df = df[["tic", "date", "fiscal_date",
             "epsActual", "epsEstimated", 
             "revenueActual", "revenueEstimated", 
             "session", "source", 
             "raw_json", "raw_json_sha256"]]
    df = df.rename(columns={
        "date": "earnings_date",
        "epsActual": "eps",
        "epsEstimated": "eps_estimated",
        "revenueActual": "revenue",
        "revenueEstimated": "revenue_estimated"
    })
    df = fix_data_types(df)
    return df

def fix_data_types(df):
    df['tic'] = df['tic'].astype(str)
    df['earnings_date'] = pd.to_datetime(df['earnings_date'], errors='coerce')
    df['fiscal_date'] = pd.to_datetime(df['fiscal_date'], errors='coerce')
    df['eps'] = pd.to_numeric(df['eps'], errors='coerce')
    df['eps_estimated'] = pd.to_numeric(df['eps_estimated'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['revenue_estimated'] = pd.to_numeric(df['revenue_estimated'], errors='coerce')
    df['session'] = df['session'].apply(lambda x: str(x) if pd.notnull(x) else None)
    df['source'] = df['source'].apply(lambda x: str(x) if pd.notnull(x) else None)
    return df

# Fetch historical earnings data
def fetch_records_coincodex(tic, exchange):
    if exchange == "NYQ":
        exchange = "NYSE"
    url = f"{BASE_URL_COINCODEX}?symbol={exchange}:{tic}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data from {url} for {tic}: {response.status_code}")
        raise
        # return [], None

def process_records_coincodex(raw_json, tic):
    df = pd.DataFrame(raw_json)
    df['tic'] = tic
    df["date"] = pd.to_datetime(df["date"])
    df["source"] = "coincodex"
    df.loc[:, 'raw_json'] = [json.dumps(row) for row in raw_json]
    df.loc[:, 'raw_json_sha256'] = [hash_dict(row) for row in raw_json]
    df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])
    df = df[df["eps"].notnull() | df["revenue"].notnull() | df["epsEstimated"].notnull() | df["revenueEstimated"].notnull()]
    df = df[["tic", "date", "fiscalDateEnding", 
             "eps", "epsEstimated", 
             "revenue", "revenueEstimated", 
             "time", "source",
             "raw_json", "raw_json_sha256"]]
    df = df.rename(columns={
        "date": "earnings_date",
        "fiscalDateEnding": "fiscal_date",
        "epsEstimated": "eps_estimated",
        "revenueEstimated": "revenue_estimated",
        "time": "session"
    })
    df = fix_data_types(df)
    return df

# Fetch estimated forecast earnings data
def fetch_forecast_records_defeatbeta(tic):
    ticker = Ticker(tic)
    eps_forecast = ticker.earnings_forecast()
    rev_forecast = ticker.revenue_forecast()

    if eps_forecast is None or rev_forecast is None:
        print(f"Failed to fetch forecast data for {tic}")
        return None, None
    else:
        return eps_forecast, rev_forecast

def process_forecast_records_defeatbeta(df_eps_est, df_rev_est, tic):
    eps_forecast = df_eps_est[df_eps_est["period_type"] == "quarterly"].copy()
    dict_eps_forecast = eps_forecast.to_dict(orient='records')
    eps_forecast.loc[:, 'raw_json'] = [json.dumps(row) for row in dict_eps_forecast]
    eps_forecast.loc[:, 'raw_json_sha256'] = [hash_dict(row) for row in dict_eps_forecast]
    eps_forecast = eps_forecast[["symbol", "report_date", "estimate_avg_eps", "raw_json", "raw_json_sha256"]]
    eps_forecast = eps_forecast.rename(columns={"symbol": "tic", "report_date": "fiscal_date", "estimate_avg_eps": "eps_estimated"})
    eps_forecast['fiscal_date'] = pd.to_datetime(eps_forecast['fiscal_date'])
    eps_forecast = eps_forecast.sort_values(by=["fiscal_date"])

    
    rev_forecast = df_rev_est[df_rev_est["period_type"] == "quarterly"].copy()
    dict_rev_forecast = rev_forecast.to_dict(orient='records')
    rev_forecast.loc[:, 'raw_json'] = [json.dumps(row) for row in dict_rev_forecast]
    rev_forecast.loc[:, 'raw_json_sha256'] = [hash_dict(row) for row in dict_rev_forecast]
    rev_forecast = rev_forecast[["symbol", "report_date", "estimate_avg_revenue", "raw_json", "raw_json_sha256"]]
    rev_forecast = rev_forecast.rename(columns={"symbol": "tic", "report_date": "fiscal_date", "estimate_avg_revenue": "revenue_estimated"})
    rev_forecast['fiscal_date'] = pd.to_datetime(rev_forecast['fiscal_date'])
    rev_forecast = rev_forecast.sort_values(by=["fiscal_date"])

    df = pd.merge_asof(
        eps_forecast, rev_forecast,
        left_on="fiscal_date",
        right_on="fiscal_date",
        by="tic",
        suffixes=('', '_rev'),
        direction="backward",
        allow_exact_matches=True
    )
    df['earnings_date'] = None
    df['fiscal_date'] = pd.to_datetime(df['fiscal_date'])
    df["eps"] = None
    df["revenue"] = None
    df["session"] = None
    df['source'] = "defeatbeta"

    df = df[["tic", "earnings_date", "fiscal_date", 
             "eps", "eps_estimated", 
             "revenue", "revenue_estimated", 
             "session", "source",
             "raw_json", "raw_json_sha256"]]
    df = fix_data_types(df)
    return df


def merge_all(df_fmp, df_coincodex, df_forecast=None):
    df_fmp = df_fmp.sort_values(by=["tic", "earnings_date"])
    df_coincodex = df_coincodex.sort_values(by=["tic", "earnings_date"])
    if df_forecast is not None:
        df_forecast = df_forecast.sort_values(by=["tic", "fiscal_date"])

    # If there is no CoinCodex data, just use FMP as-is to
    # avoid combining against effectively empty CoinCodex series
    # (which can trigger pandas FutureWarnings about empty entries).
    if df_coincodex is None or df_coincodex.empty:
        df = df_fmp.copy()
    else:
        df = pd.merge_asof(
            df_fmp, df_coincodex,
            left_on="earnings_date",
            right_on="earnings_date",
            by="tic",
            suffixes=('', '_coincodex'),
            direction="backward",
            allow_exact_matches=True
        )

        if df.empty:
            return df

        df['fiscal_date'] = df['fiscal_date'].combine_first(df['fiscal_date_coincodex'])
        df['session'] = df['session'].combine_first(df['session_coincodex'])
        df['source'] = df['source'].combine_first(df['source_coincodex'])
        df['eps'] = df['eps'].combine_first(df['eps_coincodex'])    
        df['eps_estimated'] = df['eps_estimated'].combine_first(df['eps_estimated_coincodex'])
        df['revenue'] = df['revenue'].combine_first(df['revenue_coincodex'])
        df['revenue_estimated'] = df['revenue_estimated'].combine_first(df['revenue_estimated_coincodex'])
        df['raw_json'] = df['raw_json'].combine_first(df['raw_json_coincodex'])
        df['raw_json_sha256'] = df['raw_json_sha256'].combine_first(df['raw_json_sha256_coincodex'])

    df['fiscal_date_est'] = df["fiscal_date"].shift(4)
    df['fiscal_date_est'] = df['fiscal_date_est'] + pd.DateOffset(years=1)
    df['fiscal_date'] = df['fiscal_date'].combine_first(df['fiscal_date_est'])
    
    df = df[["tic", "earnings_date", "fiscal_date", "session", "source", 
             "eps", "eps_estimated", "revenue", "revenue_estimated", 
             "raw_json", "raw_json_sha256"]]
    
    if df_forecast is None or df_forecast.empty:
        df = df.sort_values(by=["tic", "earnings_date"])
        return df
    
    j = 0
    i = 5
    while i > 0 and j < len(df_forecast):
        row = df.iloc[-i]
        if not pd.isna(row['eps']):
            i -= 1
            continue
        fiscal_date = row['fiscal_date']
        forecast_row = df_forecast.iloc[j]
        fiscal_date_forecast = forecast_row['fiscal_date']
        fiscal_date = pd.to_datetime(fiscal_date) 
        fiscal_date_forecast = pd.to_datetime(fiscal_date_forecast)
        if abs((fiscal_date - fiscal_date_forecast).days) < 20:
            df.at[df.index[-i], 'eps_estimated'] = forecast_row['eps_estimated']
            df.at[df.index[-i], 'revenue_estimated'] = forecast_row['revenue_estimated']
            df.at[df.index[-i], 'source'] = forecast_row['source']
            df.at[df.index[-i], 'raw_json'] = forecast_row['raw_json']
            df.at[df.index[-i], 'raw_json_sha256'] = forecast_row['raw_json_sha256']
            i -= 1
            j += 1
        elif fiscal_date > fiscal_date_forecast:
            j += 1
        else:
            i -= 1

    if j < len(df_forecast):
        df_forecast = df_forecast.iloc[j:]
        if not df_forecast.empty:
            df = pd.concat([df, df_forecast], ignore_index=True)
            df['earnings_date_est'] = df["earnings_date"].shift(4)
            df['earnings_date_est'] = df['earnings_date_est'] + pd.DateOffset(years=1)
            df['earnings_date'] = df['earnings_date'].combine_first(df['earnings_date_est'])
            df['source'] = df['source'].combine_first(df_forecast['source'])
            df['raw_json'] = df['raw_json'].combine_first(df_forecast['raw_json'])
            df['raw_json_sha256'] = df['raw_json_sha256'].combine_first(df_forecast['raw_json_sha256'])
            df = df.drop(columns=['earnings_date_est'])
    df = df.sort_values(by=["tic", "earnings_date"])
    return df
        
        



def insert_records(conn, df, tic):
    try:
        # keep only meaningful rows + must have earnings_date to compare/insert

        df = df[
            df["eps"].notnull()
            | df["revenue"].notnull()
            | df["eps_estimated"].notnull()
            | df["revenue_estimated"].notnull()
        ].copy()


        df = fix_data_types(df)
        df = df.astype(object).where(pd.notnull(df), None)
        query = """
        INSERT INTO raw.earnings (
            tic, calendar_year, calendar_quarter, earnings_date, fiscal_date,
            session, eps, eps_estimated, revenue, revenue_estimated,
            source, raw_json, raw_json_sha256
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tic, calendar_year, calendar_quarter)
        DO UPDATE SET
            earnings_date = EXCLUDED.earnings_date,
            fiscal_date = EXCLUDED.fiscal_date,
            session = EXCLUDED.session,
            eps = EXCLUDED.eps,
            eps_estimated = EXCLUDED.eps_estimated,
            revenue = EXCLUDED.revenue,
            revenue_estimated = EXCLUDED.revenue_estimated,
            source = EXCLUDED.source,
            raw_json = EXCLUDED.raw_json,
            raw_json_sha256 = EXCLUDED.raw_json_sha256,
            updated_at = NOW()
        WHERE 
            raw.earnings.raw_json_sha256 IS DISTINCT FROM EXCLUDED.raw_json_sha256;
        """

        params = [
            (
                row["tic"],
                row["calendar_year"],
                row["calendar_quarter"],
                row["earnings_date"],
                row["fiscal_date"],
                row["session"],
                row["eps"],
                row["eps_estimated"],
                row["revenue"],
                row["revenue_estimated"],
                row["source"],
                row["raw_json"],
                row["raw_json_sha256"],
            )
            for _, row in df.iterrows()
        ]

        # with conn.cursor() as cur:
        #     cur.executemany(query, params)
        #     total_records = cur.rowcount
        total_records = 0
        with conn.cursor() as cur:  
            for param in params:
                try:
                    cur.execute(query, param)
                    total_records += cur.rowcount
                except Exception as e:
                    print(f"Error inserting row: {param}")
                    print(f"Error: {e}")
            

        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting row: {param}")
        print(f"Error inserting earnings data for {tic}: {e}")
        conn.rollback()
        return 0




if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic, exchange FROM core.stock_profiles;")
        records = cursor.fetchall()
        for tic, exchange in records:
            data, url = fetch_records_fmp(tic)
            df_fmp = process_records_fmp(data, tic)
            
            data, url = fetch_records_coincodex(tic, exchange)
            df_coincodex = process_records_coincodex(data, tic)
            
            # eps_forecast, rev_forecast = fetch_forecast_records_defeatbeta(tic)
            # df_forecast = process_forecast_records_defeatbeta(eps_forecast, rev_forecast, tic)

            df = merge_all(df_fmp, df_coincodex, None)
            df = filter_complete_years(df, tic)
            calendar_year, calendar_quarter = zip(*[get_calendar_year_quarter(date) for date in df['earnings_date']])
            df.loc[:, 'calendar_year'] = calendar_year
            df.loc[:, 'calendar_quarter'] = calendar_quarter
            
            total_records = insert_records(conn, df, tic)
        
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()
