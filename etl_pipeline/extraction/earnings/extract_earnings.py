import requests
from psycopg import connect
from etl_pipeline.utils import hash_dict, hash_text
from database.utils import connect_to_db
import os
import pandas as pd
import json

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
        print(f"Failed to fetch data for {tic}: {response.status_code}")
        return [], None

# Insert historical earnings data into the database
def insert_records_fmp(conn, data, tic, url):
    try:

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        # df = df[df["date"] >= pd.to_datetime("2010-01-01")]
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings (
            tic, earnings_date, fiscal_date,
            session, eps, eps_estimated, revenue, revenue_estimated, 
            price_before, price_after, source, raw_json, raw_json_sha256
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, earnings_date)
        DO UPDATE SET
            fiscal_date = EXCLUDED.fiscal_date,
            session = EXCLUDED.session,
            eps = EXCLUDED.eps,
            eps_estimated = EXCLUDED.eps_estimated,
            revenue = EXCLUDED.revenue,
            revenue_estimated = EXCLUDED.revenue_estimated,
            price_before = EXCLUDED.price_before,
            price_after = EXCLUDED.price_after,
            source = EXCLUDED.source,
            raw_json = EXCLUDED.raw_json,
            raw_json_sha256 = EXCLUDED.raw_json_sha256,
            updated_at = NOW()
        WHERE 
            raw.earnings.raw_json_sha256 <> EXCLUDED.raw_json_sha256;
        """
        total_records = 0
        for i in range(len(df)):
            # earnings_date = record.get("date")
            # earnings_date = pd.to_datetime(earnings_date)

            # calendar_year = earnings_date.year
            # calendar_month = earnings_date.month
            # if calendar_month in [3, 4, 5]:
            #     calendar_quarter = 1
            # elif calendar_month in [6, 7, 8]:
            #     calendar_quarter = 2
            # elif calendar_month in [9, 10, 11]:
            #     calendar_quarter = 3
            # elif calendar_month in [12]:
            #     calendar_quarter = 4
            # elif calendar_month in [1, 2]:
            #     calendar_quarter = 4
            #     calendar_year -= 1
            # else:
            #     print(f"Unexpected earnings date {earnings_date} for ticker {tic}")
            #     continue

            cursor.execute(query, (
                tic,
                df.iloc[i]["date"],
                None,
                None,
                df.iloc[i].get("epsActual"),
                df.iloc[i].get("epsEstimated"),
                df.iloc[i].get("revenueActual"),
                df.iloc[i].get("revenueEstimated"),
                None,
                None,
                url,
                json.dumps(data[i]),
                hash_dict(data[i])
            ))
            total_records += cursor.rowcount
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting data for {tic}: {e}")
        conn.rollback()
        return 0 


# Fetch historical earnings data
def fetch_records_coincodex(tic, exchange):
    url = f"{BASE_URL_COINCODEX}?symbol={exchange}:{tic}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data for {tic}: {response.status_code}")
        return [], None

# Insert historical earnings data into the database
def insert_records_coincodex(conn, data, tic, url):
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.earnings (
            tic, earnings_date, fiscal_date,
            session, eps, eps_estimated, revenue, revenue_estimated, 
            price_before, price_after, source, raw_json, raw_json_sha256
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic, earnings_date)
        DO UPDATE SET
            fiscal_date = EXCLUDED.fiscal_date,
            session = EXCLUDED.session,
            eps = EXCLUDED.eps,
            eps_estimated = EXCLUDED.eps_estimated,
            revenue = EXCLUDED.revenue,
            revenue_estimated = EXCLUDED.revenue_estimated,
            price_before = EXCLUDED.price_before,
            price_after = EXCLUDED.price_after,
            source = EXCLUDED.source,
            raw_json = EXCLUDED.raw_json,
            raw_json_sha256 = EXCLUDED.raw_json_sha256,
            updated_at = NOW()
        WHERE 
            raw.earnings.source = EXCLUDED.source 
            AND raw.earnings.raw_json_sha256 IS DISTINCT FROM EXCLUDED.raw_json_sha256;
        """
        total_records = 0
        for record in data:
            cursor.execute(query, (
                tic,
                record.get("date"),
                record.get("fiscalDateEnding"),
                record.get("time") if pd.notnull(record.get("time")) else None,
                record.get("eps") if pd.notnull(record.get("eps")) else None,
                record.get("epsEstimated") if pd.notnull(record.get("epsEstimated")) else None,
                record.get("revenue") if pd.notnull(record.get("revenue")) else None,
                record.get("revenueEstimated") if pd.notnull(record.get("revenueEstimated")) else None,
                record.get("priceBefore") if pd.notnull(record.get("priceBefore")) else None,
                record.get("priceAfter") if pd.notnull(record.get("priceAfter")) else None,
                url,
                json.dumps(record),
                hash_dict(record)
            ))
            total_records += cursor.rowcount
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting data for {tic}: {e}")
        conn.rollback()
        return 0

# Insert historical earnings data into the database
def update_records_coincodex(conn, data, tic, url):
    try:
        cursor = conn.cursor()
        query = """
        UPDATE raw.earnings
        SET
            fiscal_date        = COALESCE(fiscal_date,        %s),
            session            = COALESCE(session,            %s),
            eps                = COALESCE(eps,                %s),
            eps_estimated      = COALESCE(eps_estimated,      %s),
            revenue            = COALESCE(revenue,            %s),
            revenue_estimated  = COALESCE(revenue_estimated,  %s),
            price_before       = COALESCE(price_before,       %s),
            price_after        = COALESCE(price_after,        %s),
            updated_at         = NOW()
        WHERE tic = %s AND earnings_date = %s;
        """
        total_records = 0
        for record in data:

            cursor.execute(query, (
                record.get("fiscalDateEnding"),
                record.get("time") if pd.notnull(record.get("time")) else None,
                record.get("eps") if pd.notnull(record.get("eps")) else None,
                record.get("epsEstimated") if pd.notnull(record.get("epsEstimated")) else None,
                record.get("revenue") if pd.notnull(record.get("revenue")) else None,
                record.get("revenueEstimated") if pd.notnull(record.get("revenueEstimated")) else None,
                record.get("priceBefore") if pd.notnull(record.get("priceBefore")) else None,
                record.get("priceAfter") if pd.notnull(record.get("priceAfter")) else None,
                tic,
                record.get("date"),
            ))
            total_records += cursor.rowcount
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting data for {tic}: {e}")
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
            total_records_fmp = insert_records_fmp(conn, data, tic, url)
            data, url = fetch_records_coincodex(tic, exchange)
            # total_records_coincodex = insert_records_coincodex(conn, data, tic, url)
            total_updated_records_coincodex = update_records_coincodex(conn, data, tic, url)

            print(f"For {tic}: Total records processed - Insert/Update {total_records_fmp} (FMP) + Update {total_updated_records_coincodex} (Coincodex);")
        conn.close()
