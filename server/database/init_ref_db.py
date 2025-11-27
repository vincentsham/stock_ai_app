from psycopg import connect
from utils import connect_to_db

# Connect to PostgreSQL
def table_creation(conn):
    try:
        cursor = conn.cursor()


        # Test the connection by executing a simple query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print("Connection test successful!")
        else:
            print("Connection test failed!")

        # Create schema 'ref' if it does not exist
        cursor.execute("""CREATE SCHEMA IF NOT EXISTS ref;""")
        print("Schema 'ref' created or already exists.")

        # Create a table for stock profiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref.analyst_grade_mapping (
            grade_original     TEXT NOT NULL,    
            grade_normalized   TEXT NOT NULL,       
            grade_value        SMALLINT NOT NULL,
            -- Embedding vector
            embedding       VECTOR(1536) NOT NULL,
            embedding_model TEXT NOT NULL,

            updated_at      TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (grade_original, embedding_model)
        );
        """)
        print("Table 'analyst_grade_mapping' created or already exists.")

       

        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            print("Tables created successfully!")
            conn.close()


if __name__ == "__main__":
    conn = connect_to_db()
    table_creation(conn)