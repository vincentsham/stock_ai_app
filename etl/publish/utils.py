from database.utils import connect_to_db



# Main function to process and load chunks
def delete_published_records(conn, table_name: str, as_of_date: str, commit=True) -> int:
    sql = f"""
        DELETE FROM {table_name}
        WHERE as_of_date = %s;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (as_of_date,))
            total_records = cursor.rowcount
        if commit:
            conn.commit()
        return total_records
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting records: {e}")
        return 0
    
