import pandas as pd
from typing import Optional
from dotenv import load_dotenv
import os
from psycopg import connect
import numpy as np

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

def read_sql_query(query: str, conn) -> pd.DataFrame:
    """Execute a SQL query and return the results as a pandas DataFrame."""
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)
            return df
    except Exception as e:
        print(f"Error executing query: {e}")
        raise e


def insert_records(conn, df: pd.DataFrame, table_name: str, keys: list[str]=[]) -> int:
    """
    Fast and minimal insert/upsert using psycopg cursor.execute with tuples.
    """
    # Replace NaN/NA with None for PostgreSQL compatibility
    df = df.replace({pd.NA: None, float('nan'): None, np.nan: None})

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])
    keys = ", ".join(keys) if len(keys) > 0 else None
    if keys:
        update_sql = f"""
        ON CONFLICT ({keys})
        DO UPDATE SET {updates}, updated_at = NOW();
        """
    else:
        update_sql = "ON CONFLICT DO NOTHING;"

    sql = f"""
        INSERT INTO {table_name} ({', '.join(cols)})
        VALUES ({placeholders})
        {update_sql};
    """

    try:
        with conn.cursor() as cursor:
            # Convert DataFrame to a sequence of tuples and execute in bulk
            data = tuple(df.itertuples(index=False, name=None))
            cursor.executemany(sql, data)  # ✅ psycopg safe bulk method

            total_records = cursor.rowcount
        conn.commit()
        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting earnings metrics: {e}")
        return 0


def insert_record(conn, df: pd.DataFrame, table_name: str, keys: list[str]=[]) -> int:
    """
    Fast and minimal insert/upsert using psycopg cursor.execute with tuples.
    """
    # Replace NaN/NA with None for PostgreSQL compatibility
    df = df.replace({pd.NA: None, float('nan'): None, np.nan: None})

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])
    keys = ", ".join(keys) if len(keys) > 0 else None
    if keys:
        update_sql = f"""
        ON CONFLICT ({keys})
        DO UPDATE SET {updates}, updated_at = NOW();
        """
    else:
        update_sql = "ON CONFLICT DO NOTHING;"

    sql = f"""
        INSERT INTO {table_name} ({', '.join(cols)})
        VALUES ({placeholders})
        {update_sql};
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, df)  # ✅ psycopg safe bulk method

            total_records = cursor.rowcount
        conn.commit()
        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting earnings metrics: {e}")
        return 0

    