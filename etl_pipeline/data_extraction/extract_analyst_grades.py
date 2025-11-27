import requests
import os
from psycopg import connect
from server.database.utils import connect_to_db
import json
from etl_pipeline.utils import hash_dict, none_if_empty


# API credentials
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable/grades-news"


# Fetching data
def fetch_records(tic, page=0, limit=100):
    url = f"{BASE_URL}?symbol={tic}&page={page}&limit={limit}&apikey={API_KEY}"
    response = requests.get(url)
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

                cur.execute("""
                    INSERT INTO raw.analyst_grades (
                        tic, published_at, title, 
                        site, company, 
                        new_grade, previous_grade, 
                        action, price_when_posted, url, 
                        source, raw_json, raw_json_sha256, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                    ON CONFLICT (tic, url) DO UPDATE SET
                        published_at = EXCLUDED.published_at,
                        title = EXCLUDED.title,
                        site = EXCLUDED.site,
                        company = EXCLUDED.company,
                        new_grade = EXCLUDED.new_grade,
                        previous_grade = EXCLUDED.previous_grade,
                        action = EXCLUDED.action,
                        price_when_posted = EXCLUDED.price_when_posted,
                        source = EXCLUDED.source,
                        raw_json = EXCLUDED.raw_json,
                        raw_json_sha256 = EXCLUDED.raw_json_sha256,
                        updated_at = NOW()
                    WHERE raw.analyst_grades.raw_json_sha256 <> EXCLUDED.raw_json_sha256
                        AND raw.analyst_grades.published_at < EXCLUDED.published_at;
                """,
                (
                    tic,
                    none_if_empty(record.get("publishedDate")),
                    none_if_empty(record.get("newsTitle")),
                    none_if_empty(record.get("newsPublisher")),
                    none_if_empty(record.get("gradingCompany")),
                    none_if_empty(record.get("newGrade")),
                    none_if_empty(record.get("previousGrade")),
                    none_if_empty(record.get("action")),
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
        print(f"Error inserting or updating analyst grades: {e}")
        conn.rollback()
        return 0
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
            for page in range(10):  # Fetch up to 10 pages
                data, url = fetch_records(tic=tic, page=page, limit=100)
                print(f"Fetched {len(data) if data else 0} records for {tic} on page {page}")
                if data:
                    total_records += insert_records(data, tic, url,conn)
                else:
                    break  # Stop if no more data

            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()

if __name__ == "__main__":
    main()