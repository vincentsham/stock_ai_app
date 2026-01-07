
import pandas as pd
import numpy as np
from database.utils import connect_to_db, insert_records, execute_query
from utils import delete_published_records
from etl.utils import fix_quotes



def read_records(tic):
    """
    Reads data from the core.earnings table and returns it as a pandas DataFrame.
    """
    query = f"""
        SELECT 
            eta.inference_id,
            eta.event_id,
            eta.tic,
            eta.calendar_year,
            eta.calendar_quarter,
            et.earnings_date,
            eta.sentiment,
            eta.durability,
            eta.performance_factors,
            eta.past_summary,
            eta.guidance_direction,
            eta.revenue_outlook,
            eta.margin_outlook,
            eta.earnings_outlook,
            eta.cashflow_outlook,
            eta.growth_acceleration,
            eta.future_outlook_sentiment,
            eta.growth_drivers,
            eta.future_summary,
            eta.risk_mentioned,
            eta.risk_impact,
            eta.risk_time_horizon,
            eta.risk_factors,
            eta.risk_summary,
            eta.mitigation_mentioned,
            eta.mitigation_effectiveness,
            eta.mitigation_time_horizon,
            eta.mitigation_actions,
            eta.mitigation_summary,
            eta.transcript_sha256,
            eta.updated_at
        FROM core.earnings_transcript_analysis eta
        JOIN core.earnings_transcripts et 
        ON eta.event_id = et.event_id
        WHERE eta.tic = '{tic}';
    """

    # Connect to the database
    df = execute_query(query)
    return df



def main():
    """
    Main function to orchestrate the ETL process for earnings.
    """
    conn_local = connect_to_db("localhost")
    conn_supabase = connect_to_db("supabase")
    if conn_local and conn_supabase:
        cursor = conn_local.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        today = pd.Timestamp.now().date()
        try:
            total_deleted = delete_published_records(conn_local, "mart.earnings_transcript_analysis", today, commit=False)
            delete_published_records(conn_supabase, "mart.earnings_transcript_analysis", today, commit=False)
            print(f"Deleted {total_deleted} records from mart.earnings_transcript_analysis for as_of_date = {today}")
            for record in records:
                tic = record[0]
                df = read_records(tic)
                df['as_of_date'] = today
                df['past_summary'] = df['past_summary'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                df['future_summary'] = df['future_summary'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                df['risk_summary'] = df['risk_summary'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                df['mitigation_summary'] = df['mitigation_summary'].apply(lambda x: fix_quotes(x) if isinstance(x, str) else x)
                
                cols = ['inference_id', 'event_id',
                        'tic', 'calendar_year', 'calendar_quarter', 'earnings_date', 
                        'sentiment', 'durability', 'performance_factors',
                        'past_summary', 'guidance_direction', 'revenue_outlook',
                        'margin_outlook', 'earnings_outlook', 'cashflow_outlook',
                        'growth_acceleration', 'future_outlook_sentiment', 'growth_drivers',
                        'future_summary', 'risk_mentioned', 'risk_impact',
                        'risk_time_horizon', 'risk_factors', 'risk_summary',
                        'mitigation_mentioned', 'mitigation_effectiveness', 'mitigation_time_horizon',
                        'mitigation_actions', 'mitigation_summary',
                        'transcript_sha256', 'updated_at', 'as_of_date'
                        ]
                df = df[cols]
                total_inserted = insert_records(conn_local, df, "mart.earnings_transcript_analysis", 
                                            ["tic", "calendar_year", "calendar_quarter", "as_of_date"], 
                                            updated_at=False, commit=False,
                                            batch_size=10)
                insert_records(conn_supabase, df, "mart.earnings_transcript_analysis", 
                                            ["tic", "calendar_year", "calendar_quarter", "as_of_date"], 
                                            updated_at=False, commit=False,
                                            batch_size=10)
                print(f"For {tic}: Total records inserted = {total_inserted}")
        except Exception as e:
            print(f"Error processing earnings_transcript_analysis data: {e}")
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