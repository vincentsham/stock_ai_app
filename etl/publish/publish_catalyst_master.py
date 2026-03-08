
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
from etl.utils import fix_quotes
import os
app_env = os.getenv("APP_ENV", "local")


def read_records(tic):
    """
    Reads data from the core.catalyst_master table and returns it as a pandas DataFrame.
    """
    query = f"""
        WITH chunk_lookup AS (
            -- News chunks
            SELECT
                nc.chunk_id::text AS chunk_id,
                nc.url,
                'news article' AS source_type
            FROM core.news_chunks AS nc
            WHERE nc.tic = '{tic}'

            UNION ALL

            -- Earnings transcript chunks
            SELECT
                etc.chunk_id::text AS chunk_id,
                NULL AS url,
                'earnings transcript (Q' || etc.calendar_quarter || ' ' || etc.calendar_year || ')' AS source_type
            FROM core.earnings_transcript_chunks AS etc
            WHERE etc.tic = '{tic}'
        )
        SELECT
            cm.catalyst_id,
            cm.tic,
            cm.date,
            cm.catalyst_type,
            cm.title,
            cm.summary,
            cm.sentiment,
            cm.time_horizon,
            cm.magnitude,
            cm.impact_area,
            cm.mention_count,
            cm.chunk_ids,
            cm.citations,
            COALESCE(cl.source_types, ARRAY[]::text[]) AS source_types,
            COALESCE(cl.urls, ARRAY[]::text[])         AS urls,
            cm.created_at,
            cm.updated_at
        FROM core.catalyst_master AS cm
        LEFT JOIN LATERAL (
            SELECT
                array_agg(c.source_type) AS source_types,
                array_agg(c.url) FILTER (WHERE c.url IS NOT NULL) AS urls
            FROM chunk_lookup AS c
            WHERE c.chunk_id = ANY(cm.chunk_ids)
        ) AS cl ON TRUE
        WHERE cm.tic = '{tic}' AND cm.mention_count > 0 AND (cm.sentiment = 1 OR cm.sentiment = -1)
        ORDER BY date DESC, magnitude DESC, updated_at DESC, catalyst_id DESC;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for catalyst master.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.catalyst_master", today, commit=False)
            delete_published_records(conn_supabase, "mart.catalyst_master", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.catalyst_master for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                # Remove "Delta: "
                df['summary'] = df['summary'].str.replace("delta: ", "", case=False, regex=False)
                df['summary'] = df['summary'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                df['title'] = df['title'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                df['citations'] = df['citations'].apply(lambda x: [fix_quotes(item) for item in x] if isinstance(x, list) else x)
                df['as_of_date'] = today
                cols = ['catalyst_id', 'tic', 'date', 'catalyst_type', 'title', 'summary',
                        'sentiment', 'time_horizon', 'magnitude',
                        'impact_area', 'mention_count', 'chunk_ids', 'source_types', 'citations', 'urls', 
                        'created_at', 'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.catalyst_master", 
                                            ["catalyst_id", "as_of_date"], 
                                            updated_at=False, commit=False,
                                            batch_size=10)
                insert_records(conn_supabase, df, "mart.catalyst_master", 
                                            ["catalyst_id", "as_of_date"], 
                                            updated_at=False, commit=False,
                                            batch_size=10)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing catalyst master data: {e}")
            conn_local.rollback()
            conn_local.close()
            conn_supabase.rollback()
            conn_supabase.close()
            return
        conn_local.commit()
        conn_local.close()
        conn_supabase.commit()
        conn_supabase.close()
        return
    return


if __name__ == "__main__":
    main()