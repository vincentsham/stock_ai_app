import os
import sys
from psycopg import connect
import database.config


def test_connection():
    # 1. Fetch Variable
    connection_string = os.getenv("PGCONNECTION_SESSION")

    # 2. Debug: Check if missing
    if not connection_string:
        print("❌ ERROR: Missing environment variable 'PGCONNECTION_SESSION'")
        return None

    try:
        # 3. Connect (Using your exact parameters)
        conn = connect(
            connection_string, 
            connect_timeout=120, 
            keepalives=1, 
            keepalives_idle=30, 
            keepalives_interval=10, 
            keepalives_count=5,
            sslmode='require'
        )
        print("✅ Connection Successful!")
        
        # 4. Check for the "Fail Message" you wanted
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM mart.stock_scores;")
        count = cur.fetchone()[0]
        print(f"📊 Rows in mart.stock_scores table: {count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        # This will catch the "relation does not exist" error you want to see
        print(f"❌ Connection/Query Failed: {e}")

if __name__ == "__main__":
    test_connection()