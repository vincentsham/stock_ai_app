
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records



def read_records(tic):
    """
    Reads data from the core.catalyst_master table and returns it as a pandas DataFrame.
    """
    query = f"""
        WITH catalyst_events AS (
            SELECT
                cv.event_id,
                cv.catalyst_id,
                cv.evidence,
                COALESCE(
                    CASE
                        WHEN cv.source_type = 'earnings_transcript'
                            THEN 'earnings transcript (Q' || et.calendar_quarter || ' ' || et.calendar_year || ')'
                        ELSE 'news article'
                    END,
                    'unknown'
                ) AS source_type,
                cv.url
            FROM core.catalyst_versions AS cv
            LEFT JOIN (
                SELECT event_id, calendar_quarter, calendar_year
                FROM core.earnings_transcripts
                WHERE tic = '{tic}'
            ) AS et
                ON cv.event_id = et.event_id
            WHERE cv.is_valid = 1 AND cv.tic = '{tic}'
        )
        SELECT
            cm.catalyst_id,
            cm.tic,
            cm.date,
            cm.catalyst_type,
            cm.title,
            cm.summary,
            cm.state,
            cm.sentiment,
            cm.time_horizon,
            cm.impact_magnitude,
            cm.certainty,
            cm.impact_area,
            cm.mention_count,
            cm.event_ids,
            COALESCE(ev.source_types, ARRAY[]::text[])   AS source_types,
            COALESCE(ev.evidences, ARRAY[]::text[])      AS evidences,
            COALESCE(ev.urls, ARRAY[]::text[])     AS urls,
            cm.created_at,
            cm.updated_at
        FROM core.catalyst_master AS cm
        LEFT JOIN LATERAL (
            SELECT
                array_agg(ce.source_type ORDER BY ce.event_id) AS source_types,
                array_agg(ce.evidence ORDER BY ce.event_id)    AS evidences,
                array_agg(ce.url ORDER BY ce.event_id)   AS urls
            FROM catalyst_events AS ce
            WHERE ce.catalyst_id = cm.catalyst_id AND ce.event_id::text = ANY(cm.event_ids)
        ) AS ev ON TRUE
        WHERE cm.tic = '{tic}' AND cm.mention_count > 0 AND (cm.sentiment = 1 OR cm.sentiment = -1)
        ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for catalyst master.
    """
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn, "mart.catalyst_master", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.catalyst_master for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                cols = ['catalyst_id', 'tic', 'date', 'catalyst_type', 'title', 'summary',
                        'state', 'sentiment', 'time_horizon', 'impact_magnitude', 'certainty',
                        'impact_area', 'mention_count', 'event_ids', 'source_types', 'evidences', 'urls', 
                        'created_at', 'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn, df, "mart.catalyst_master", 
                                            ["catalyst_id", "as_of_date"], 
                                            updated_at=False, commit=False)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing catalyst master data: {e}")
            conn.rollback()
            conn.close()
            return
        conn.commit()
        conn.close()
        return
    return


if __name__ == "__main__":
    main()