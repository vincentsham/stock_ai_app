import requests
import os
from psycopg import connect
from server.database.utils import connect_to_db
import json


# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/news/stock"


# Fetching news data
def fetch_news(tic, limit=100):
    url = f"{BASE_URL}?symbols={tic}&limit={limit}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

# Insert news data into the table
def insert_news(data, tic, url, conn):
    total_records = 0
    try:
        with conn.cursor() as cur:
            for record in data:
                cur.execute("""
                    INSERT INTO raw.news (
                        tic, published_date, publisher, title, site, content, url, raw_json, source
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tic, url) DO UPDATE
                    SET publisher = EXCLUDED.publisher,
                        title = EXCLUDED.title,
                        site = EXCLUDED.site,
                        content = EXCLUDED.content,
                        raw_json = EXCLUDED.raw_json,
                        source = EXCLUDED.source;
                """, (
                    tic,
                    record.get("publishedDate"),
                    record.get("publisher"),
                    record.get("title"),
                    record.get("site"),
                    record.get("text"),
                    record.get("url"),
                    json.dumps(record),  # raw JSON payload
                    url
                ))
                total_records += cur.rowcount
            conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting or updating data for ticker {tic}: {e}")
        conn.rollback()
        return 0

# Main function
def main():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM stock_metadata;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            total_records = 0
            data, url = fetch_news(tic=tic, limit=100)
            if data:
                total_records += insert_news(data, tic, url, conn)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()