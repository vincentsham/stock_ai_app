import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query


def read_records():
    """
    Reads data from the raw.analyst_price_targets table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT r.tic, r.url, r.source, r.raw_json, r.raw_json_sha256
    FROM raw.analyst_price_targets as r
    LEFT JOIN core.analyst_price_targets as c
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
    Transforms the raw analyst price targets data to match the schema of core.analyst_price_targets.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw analyst price targets data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.analyst_price_targets schema.
    """
    transformed_df = pd.DataFrame()

    # Map columns from raw to core schema
    for i in range(len(raw_df)):

        """
         CREATE TABLE IF NOT EXISTS core.analyst_price_targets (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            title        text,
            site    text,
                       
            analyst_name      text,
            company   text,
            price_target      numeric(12,2),
            adj_price_target  numeric(12,2),
            price_when_posted numeric(12,4),

            url              text NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, url)
        );

        {'symbol': 'NVDA',
        'newsURL': 'https://thefly.com/permalinks/entry.php/id4213792/5313286394/NVDA-HSBC-upgrades-Nvidia-to-Buy-on-earnings-upside-potential',
        'newsTitle': 'HSBC upgrades Nvidia to Buy on earnings upside potential',
        'analystName': '',
        'newsBaseURL': 'thefly.com',
        'priceTarget': 320,
        'newsPublisher': 'TheFly',
        'publishedDate': '2025-10-15T10:22:14.000Z',
        'adjPriceTarget': 320,
        'analystCompany': 'UBS',
        'priceWhenPosted': 180.03}
        """
    
        data = raw_df.iloc[i]['raw_json']

        transformed_df.at[i, 'tic'] = raw_df.iloc[i]['tic']
        transformed_df.at[i, 'published_at'] = data.get('publishedDate', None)
        transformed_df.at[i, 'title'] = data.get('newsTitle', None)
        transformed_df.at[i, 'analyst_name'] = data.get('analystName', None)
        transformed_df.at[i, 'site'] = data.get('newsPublisher', None)
        transformed_df.at[i, 'company'] = data.get('analystCompany', None)
        transformed_df.at[i, 'price_target'] = data.get('priceTarget', None)
        transformed_df.at[i, 'adj_price_target'] = data.get('adjPriceTarget', None)
        transformed_df.at[i, 'price_when_posted'] = data.get('priceWhenPosted', None)

        transformed_df.at[i, 'url'] = raw_df.iloc[i]['url']
        transformed_df.at[i, 'source'] = raw_df.iloc[i]['source']
        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    return transformed_df



def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.analyst_price_targets table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.analyst_price_targets schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.analyst_price_targets
        total_records = insert_records(conn, transformed_df, 'core.analyst_price_targets', ['tic', 'url'])
        print(f"Total records inserted/updated in core.analyst_price_targets: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for analyst price targets.
    """
    # Step 1: Read raw analyst price targets data
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)

    # Step 3: Load the transformed data into core.news
    load_records(transformed_df)

if __name__ == "__main__":
    main()