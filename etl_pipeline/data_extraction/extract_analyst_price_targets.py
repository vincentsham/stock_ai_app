import requests
import os
from psycopg import connect
from server.database.utils import connect_to_db
import json
from etl_pipeline.utils import none_if_empty, hash_dict


# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/price-target-news"


# Fetching data
def fetch_records(tic, page=0, limit=100):
    url = f"{BASE_URL}?symbol={tic}&page={page}&limit={limit}"
    response = requests.get(url + f"&apikey={API_KEY}")

    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None


# Insert data into the table
def insert_records(data, tic, url, conn):
    total_records = 0
    try:
        with conn.cursor() as cur:
            for record in data:
                # Map API fields to DB columns
                cur.execute("""
                    INSERT INTO raw.analyst_price_targets (
                        tic, published_at, news_title, news_base_url, news_publisher, 
                        analyst_name, broker, price_target, adj_price_target, 
                        price_when_posted, url, source, raw_json, raw_json_sha256, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                    ON CONFLICT (tic, url) DO UPDATE SET
                        published_at = EXCLUDED.published_at,
                        news_title = EXCLUDED.news_title,
                        news_base_url = EXCLUDED.news_base_url,
                        news_publisher = EXCLUDED.news_publisher,
                        analyst_name = EXCLUDED.analyst_name,
                        broker = EXCLUDED.broker,
                        price_target = EXCLUDED.price_target,
                        adj_price_target = EXCLUDED.adj_price_target,
                        price_when_posted = EXCLUDED.price_when_posted,
                        source = EXCLUDED.source,
                        raw_json = EXCLUDED.raw_json,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW()
                    WHERE raw.analyst_price_targets.raw_json_sha256 <> EXCLUDED.raw_json_sha256;
                """,
                (
                    tic,
                    none_if_empty(record.get("publishedDate")),
                    none_if_empty(record.get("newsTitle")),
                    none_if_empty(record.get("newsBaseURL")),
                    none_if_empty(record.get("newsPublisher")),
                    none_if_empty(record.get("analystName")),
                    none_if_empty(record.get("analystCompany")),
                    none_if_empty(record.get("priceTarget")),
                    none_if_empty(record.get("adjPriceTarget")),
                    none_if_empty(record.get("priceWhenPosted")),
                    none_if_empty(record.get("newsURL")),
                    url,
                    json.dumps(record),
                    hash_dict(record)
                ))
                total_records += cur.rowcount
            conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting or updating analyst price targets: {e}")
        conn.rollback()
        return 0

# Main function
def main():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            total_records = 0
            # You can page through results if needed
            data, url = fetch_records(tic=tic, page=0, limit=100)
            if data:
                total_records += insert_records(data, tic, url,conn)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()