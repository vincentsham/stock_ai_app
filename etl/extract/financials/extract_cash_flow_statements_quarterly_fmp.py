import requests
import os
from psycopg import connect
from database.utils import connect_to_db, insert_records
import json
from etl.utils import hash_dict, filter_complete_years, get_fiscal_year_quarter
import pandas as pd


# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/cash-flow-statement"


# Fetching data
def fetch_records(tic, period, limit=5):
    url = f"{BASE_URL}?symbol={tic}&limit={limit}&period={period}"
    response = requests.get(url + f"&apikey={API_KEY}")
    source = 'fmp'
    if response.status_code == 200:
        return response.json(), source
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

# Main function
def main():
    conn = connect_to_db()
    if conn:
        sql = """
            SELECT tic FROM core.stock_profiles;
        """
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            total_records = 0
            df = {}
            data = []
            source = []
            for period in ["Q1", "Q2", "Q3", "Q4"]:
                _data, _source = fetch_records(tic=tic, period=period, limit=5)
                data.extend(_data if _data else [])
                source.extend([_source] * len(_data) if _data else [])

            if len(data) > 0:
                df['tic'] = tic
                df['fiscal_date'] = [pd.to_datetime(item.get("date")) for item in data]
                df['source'] = source
                df['raw_json'] = [json.dumps(item) for item in data]
                df['raw_json_sha256'] = [hash_dict(item) for item in data]
                df = pd.DataFrame(df)
                df['fiscal_year'] = [int(item.get("fiscalYear")) for item in data]
                df['fiscal_quarter'] = [int(item.get("period")[1]) for item in data]
                df = filter_complete_years(df, tic, date_col=None, year_col='fiscal_year', quarter_col='fiscal_quarter')


                total_records += insert_records(conn, df, "raw.cash_flow_statements_quarterly",
                                                ["tic", "fiscal_year", "fiscal_quarter", "source"], 
                                                where=["raw_json_sha256"])
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()