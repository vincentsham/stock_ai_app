import pandas as pd
from typing import Optional
from dotenv import load_dotenv
import os
from psycopg import connect
import numpy as np

# Load environment variables from .env file
# 1. Look for 'APP_ENV'. If not found, default to 'local'
app_env = os.getenv("APP_ENV", "local")

# 2. Load the specific file based on the environment
if app_env == "aws":
    # This loads your RDS endpoint and 'db_admin' user
    load_dotenv(".env.aws", override=True)
else:
    # This loads 'localhost' and 'vincentsham' user
    load_dotenv(".env.local", override=True)


# Connect to PostgreSQL
def connect_to_db(type: str = "localhost"):
    try:

        if type == "localhost":
            # 1. Fetch Variables
            db_name = os.getenv("PGDATABASE")
            db_user = os.getenv("PGUSER")
            db_pass = os.getenv("PGPASSWORD")
            db_host = os.getenv("PGHOST")
            db_port = os.getenv("PGPORT")

            # 2. Debug: Check for missing values
            missing_vars = []
            if not db_name: missing_vars.append("PGDATABASE")
            if not db_user: missing_vars.append("PGUSER")
            if not db_pass: missing_vars.append("PGPASSWORD")
            if not db_host: missing_vars.append("PGHOST")
            if not db_port: missing_vars.append("PGPORT")

            if missing_vars:
                print(f"❌ ERROR: Missing environment variables for localhost: {', '.join(missing_vars)}")
                return None

            # 3. Connect
            conn = connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port
            )

        elif type == "supabase":
            # 1. Fetch Variable
            connection_string = os.getenv("PGCONNECTION_SESSION")

            # 2. Debug: Check if missing
            if not connection_string:
                print("❌ ERROR: Missing environment variable 'PGCONNECTION_SESSION'")
                return None

            # 3. Connect
            conn = connect(
                connection_string, 
                connect_timeout=120, 
                keepalives=1, 
                keepalives_idle=30, 
                keepalives_interval=10, 
                keepalives_count=5,
                sslmode='require'
            )
        else:
            raise ValueError(f"Invalid connection type specified: {type}")
        
        return conn

    except Exception as e:
        print(f"❌ Connection Failed ({type}): {e}")
        return None
    
    
    
def escape_sql_literal(val):
    if val is None:
        return None
    if isinstance(val, str):
        return val.replace("'", "''")
    # Avoid converting lists, dicts, or other non-string types to string
    return val

def escape_sql_backslash(val):
    if val is None:
        return None
    if isinstance(val, str):
        return val.replace('\\', '\\\\')
    # Avoid converting lists, dicts, or other non-string types to string
    return val

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


def insert_records(conn, df: pd.DataFrame, table_name: str, keys: list[str]=[], 
                   updated_at: bool = True, where: list[str]=[], commit=True,
                   batch_size: int = 100) -> int:
    """
    Fast and minimal insert/upsert using psycopg cursor.execute with tuples.
    """

    # apply safe_str to all string columns
    # for col in df.select_dtypes(include=['object', 'string']).columns:
    #     df.loc[:, col] = df[col].apply(escape_sql_literal)
    #     df.loc[:, col] = df[col].apply(escape_sql_backslash)

    # Replace NaN/NA with None for PostgreSQL compatibility
    df = df.astype(object)
    df = df.where(pd.notnull(df), None)

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])
    keys = ", ".join(keys) if len(keys) > 0 else None
    where_clause = ""
    if keys:
        update_sql = f"""
        ON CONFLICT ({keys})
        DO UPDATE SET {updates}
        """
        if updated_at:
            update_sql += ", updated_at = NOW()"
            if where:
                # core.earnings_transcripts.raw_json_sha256 IS DISTINCT FROM EXCLUDED.raw_json_sha256
                where_clause = " AND ".join([f"{table_name}.{col} IS DISTINCT FROM EXCLUDED.{col}" for col in where])
                where_clause = f"WHERE {where_clause}"
    else:
        update_sql = "ON CONFLICT DO NOTHING"


    sql = f"""
        INSERT INTO {table_name} ({', '.join(cols)})
        VALUES ({placeholders})
        {update_sql}
        {where_clause}
    """
    sql += ";"

    try:
        total_records = 0
        with conn.cursor() as cursor:
            # Convert DataFrame to a list of tuples (Must be a list to slice it for batches)
            data = list(df.itertuples(index=False, name=None))
            total_len = len(data)
            
            # --- BATCHING LOGIC STARTS HERE ---
            # We default to 100, but for transcripts, you might want to pass batch_size=10
            for i in range(0, total_len, batch_size):
                batch = data[i : i + batch_size]
                cursor.executemany(sql, batch)
                
                # Vital: Commit after every batch to release memory and DB locks
                if commit:
                    conn.commit()
                    
                total_records += cursor.rowcount
                # Optional: Print progress for large jobs
                if total_len > 100:
                    print(f"   - Batch {i//batch_size + 1}: Processed {min(i + batch_size, total_len)}/{total_len} rows")
            # ----------------------------------

        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting records: {e}")
        return 0


def insert_record(conn, df: pd.DataFrame, table_name: str, keys: list[str]=[], 
                  updated_at: bool = True, where: list[str]=[], commit=True) -> int:
    """
    Fast and minimal insert/upsert using psycopg cursor.execute with tuples.
    """
    # for col in df.select_dtypes(include=['object', 'string']).columns:
    #     df.loc[:, col] = df[col].apply(escape_sql_literal)
    #     df.loc[:, col] = df[col].apply(escape_sql_backslash)

    # Replace NaN/NA with None for PostgreSQL compatibility
    df = df.astype(object)
    df = df.replace({pd.NA: None, float('nan'): None, np.nan: None})

    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    updates = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])
    keys = ", ".join(keys) if len(keys) > 0 else None
    where_clause = ""
    if keys:
        update_sql = f"""
        ON CONFLICT ({keys})
        DO UPDATE SET {updates}
        """
        if updated_at:
            update_sql += ", updated_at = NOW()"
            if where:
                # core.earnings_transcripts.raw_json_sha256 IS DISTINCT FROM EXCLUDED.raw_json_sha256
                where_clause = " AND ".join([f"{table_name}.{col} IS DISTINCT FROM EXCLUDED.{col}" for col in where])
                where_clause = f"WHERE {where_clause}"
    else:
        update_sql = "ON CONFLICT DO NOTHING"

    sql = f"""
        INSERT INTO {table_name} ({', '.join(cols)})
        VALUES ({placeholders})
        {update_sql}
        {where_clause}
    """
    sql += ";"
    
    try:
        with conn.cursor() as cursor:
            df_values = tuple(df.iloc[0].tolist())
            cursor.execute(sql, df_values)  

            total_records = cursor.rowcount
        if commit:
            conn.commit()
        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting record: {e}")
        return 0

    

