import pandas as pd
from typing import Optional
from dotenv import load_dotenv
import os
from psycopg import connect

# Load environment variables from .env file
load_dotenv()

# Database credentials
DB_NAME = os.getenv("PGNAME")
DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")

# Connect to PostgreSQL
def connect_to_db():
    try:
        conn = connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def escape_sql_literal(s: str) -> str:
    """Very basic escape for SQL string literals (single quotes)."""
    return s.replace("'", "''") if s is not None else s

def execute_query(sql: str, params: Optional[dict] = None):
    """Execute a SQL query with optional parameters."""
    
    try:
        conn = connect_to_db()
        with conn.cursor() as cursor:
            if params:
                sql = sql.format(**params)
            # Fetch all records from the earnings_transcript_chunks table
            cursor.execute(sql)
            records = cursor.fetchall()

            # Create a DataFrame from the fetched records
            df = pd.DataFrame(records, columns=[desc[0] for desc in cursor.description])
            return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        conn.close()
