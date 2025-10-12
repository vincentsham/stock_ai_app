import yfinance as yf
from psycopg import connect
from psycopg.errors import UniqueViolation
from server.database.utils import connect_to_db
import json
from utils import hash_dict


# Fetch stock profiles from yfinance
def fetch_records(tickers):
    data = []
    for ticker in tickers:
        print(f"Fetching info for {ticker}...")
        stock = yf.Ticker(ticker)
        info = stock.info
        exchange = info.get("exchange")
        if exchange == "NMS":
            exchange = "NASDAQ"
        data.append((
            ticker.upper(),
            info.get("longName"),
            info.get("sector"),
            info.get("industry"),
            info.get("country"),
            info.get("marketCap"),
            info.get("fullTimeEmployees"),
            info.get("longBusinessSummary"),
            info.get("website"),
            exchange,
            info.get("currency"),
            "yfinance",
            json.dumps(info),
            hash_dict(info)
        ))
    return data

# Insert records into the database
def insert_records(conn, data):
    total_records = 0
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO raw.stock_profiles (
            tic, name, sector, industry, country, market_cap, employees, description, website, exchange, currency, source, raw_json, payload_sha256
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (tic) DO UPDATE SET
            name = EXCLUDED.name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            country = EXCLUDED.country,
            market_cap = EXCLUDED.market_cap,
            employees = EXCLUDED.employees,
            description = EXCLUDED.description,
            website = EXCLUDED.website,
            exchange = EXCLUDED.exchange,
            currency = EXCLUDED.currency,
            source = EXCLUDED.source,
            raw_json = EXCLUDED.raw_json,
            payload_sha256 = EXCLUDED.payload_sha256,
            updated_at = NOW();
        """
        for record in data:
            try:
                cursor.execute(query, record)
                total_records += cursor.rowcount
            except UniqueViolation:
                print(f"Duplicate entry for {record[0]}")
        conn.commit()
        return total_records
    except Exception as e:
        print(f"Error inserting records: {e}")
        conn.rollback()
        return 0

if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "NVDA"]
    conn = connect_to_db()
    if conn:
        records = fetch_records(tickers)
        total_records = insert_records(conn, records)
        print(f"Total records inserted: {total_records}")
        conn.close()