import requests
import os
from psycopg import connect
from database.utils import connect_to_db, insert_records
import json
from etl_pipeline.utils import hash_dict, hash_text, get_fiscal_year_quarter, filter_complete_years
from defeatbeta_api.data.ticker import Ticker
import numpy as np
import pandas as pd

# Avoid FutureWarning from pandas.replace; we’ll downcast explicitly via infer_objects().
try:
    pd.set_option("future.no_silent_downcasting", True)
except Exception:
    pass


# Fetching data
def fetch_records(tic):
    ticker = Ticker(tic)
    df = ticker.quarterly_balance_sheet()
    df = df.df().T.reset_index()
    df.columns = df.iloc[0]
    df = df[~df['Breakdown'].isin(["TTM", "Breakdown"])]
    df = df.rename(columns={"Breakdown": "date"})
    df = df.replace("*", None)
    source = "defeatbeta"
    return df, source

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
            data, source = fetch_records(tic=tic)
            df = {}
            if not data.empty:
                data = filter_complete_years(data, tic, date_col='date')
                fiscal_year, fiscal_quarter = zip(*[get_fiscal_year_quarter(date) for date in data['date']])
                df['tic'] = tic
                df['fiscal_year'] = fiscal_year
                df['fiscal_quarter'] = fiscal_quarter
                df['fiscal_date'] = pd.to_datetime(data['date'])
                df['source'] = source
                df['raw_json'] = [row.to_json() for _, row in data.iterrows()]
                df['raw_json_sha256'] = [hash_text(raw_json) for raw_json in df['raw_json']]
                df = pd.DataFrame(df)

                total_records += insert_records(conn, df, "raw.balance_sheets_quarterly",
                                                ["tic", "fiscal_year", "fiscal_quarter", "source"], 
                                                where=["raw_json_sha256"])
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()