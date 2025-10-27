import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.news table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT r.tic, r.url, r.source, r.raw_json, r.raw_json_sha256
    FROM raw.news as r
    LEFT JOIN core.news as c
    ON r.tic = c.tic
        AND r.url = c.url
    WHERE c.raw_json_sha256 IS NULL 
        OR c.raw_json_sha256 <> r.raw_json_sha256
    ;
    """

    # Connect to the database
    df = execute_query(query)

    return df


def transform_records(raw_df):
    """
    Transforms the raw news data to match the schema of core.news.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw news data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.news schema.
    """
    transformed_df = pd.DataFrame()

    # Map columns from raw to core schema
    for i in range(len(raw_df)):

        """
            tic             VARCHAR(10) NOT NULL,              -- stock ticker
            published_at  TIMESTAMP   NOT NULL,              -- from API publishedDate
            publisher       TEXT,
            title           TEXT NOT NULL,
            site            TEXT,
            content         TEXT,
            url             TEXT NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
        """

        data = raw_df.iloc[i]['raw_json']

        transformed_df.at[i, 'tic'] = raw_df.iloc[i]['tic']
        transformed_df.at[i, 'published_at'] = data.get('publishedDate', None)
        transformed_df.at[i, 'publisher'] = data.get('publisher', None)
        transformed_df.at[i, 'title'] = data.get('title', None)
        transformed_df.at[i, 'site'] = data.get('site', None)
        transformed_df.at[i, 'content'] = data.get('text', None)
        transformed_df.at[i, 'url'] = raw_df.iloc[i]['url']
        transformed_df.at[i, 'source'] = raw_df.iloc[i]['source']

        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    return transformed_df


def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.news table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.news schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.news
        total_records = insert_records(conn, transformed_df, 'core.news', ['tic', 'url'])
        print(f"Total records inserted/updated in core.news: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for news articles.
    """
    # Step 1: Read raw news articles
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.news
    load_records(transformed_df)

if __name__ == "__main__":
    main()