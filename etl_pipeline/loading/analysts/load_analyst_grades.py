import pandas as pd
import json
from database.utils import connect_to_db, insert_records, execute_query
from grade_mapping import get_mapping, classify_grade_embedding_similarity, ref_grade_list


grade_mapping = get_mapping()  
# grade_mapping example: {"Overweight": ("Buy", 1, <embedding_vector>, <embedding_model_used>), ...}


def read_records():
    """
    Reads data from the raw.analyst_grades table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT r.tic, r.url, r.source, r.raw_json, r.raw_json_sha256
    FROM raw.analyst_grades as r
    LEFT JOIN core.analyst_grades as c
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
    Transforms the raw analyst grades data to match the schema of core.analyst_grades.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw analyst grades data.

    Returns:
        pd.DataFrame: Transformed DataFrame matching core.analyst_grades schema.
    """
    transformed_df = pd.DataFrame()

    # Map columns from raw to core schema
    for i in range(len(raw_df)):

        """
        CREATE TABLE IF NOT EXISTS core.analyst_grades (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            title        text,
            site    text,
                       
            company           text,
            new_grade         SMALLINT,
            previous_grade    SMALLINT,
            action            text,
            price_when_posted numeric(12,4),

            url               text NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, url)
        );
        """
    
        data = raw_df.iloc[i]['raw_json']

        transformed_df.at[i, 'tic'] = raw_df.iloc[i]['tic']
        transformed_df.at[i, 'published_at'] = data.get('publishedDate', None)
        transformed_df.at[i, 'title'] = data.get('newsTitle', None)
        transformed_df.at[i, 'site'] = data.get('newsPublisher', None)
        transformed_df.at[i, 'company'] = data.get('gradingCompany', None)
        transformed_df.at[i, 'new_grade'] = data.get('newGrade', None)
        transformed_df.at[i, 'previous_grade'] = data.get('previousGrade', None)
        transformed_df.at[i, 'action'] = data.get('action', None)
        transformed_df.at[i, 'price_when_posted'] = data.get('priceWhenPosted', None)

        transformed_df.at[i, 'url'] = raw_df.iloc[i]['url']
        transformed_df.at[i, 'source'] = raw_df.iloc[i]['source']
        transformed_df.at[i, 'raw_json'] = json.dumps(raw_df.iloc[i]['raw_json'])
        transformed_df.at[i, 'raw_json_sha256'] = raw_df.iloc[i]['raw_json_sha256']

    return transformed_df



def normalize_analyst_grades(df):
    df['new_grade_normalized'] = df['new_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[0])
    df['new_grade_value'] = df['new_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[1])
    df['previous_grade_normalized'] = df['previous_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[0])
    df['previous_grade_value'] = df['previous_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[1])
    # Handle unmapped grades via embedding similarity classification
    if df['new_grade_normalized'].isna().any() or df['previous_grade_normalized'].isna().any():
        unclassified_new_grades = df[df['new_grade_normalized'].isna()]['new_grade']
        unclassified_previous_grades = df[df['previous_grade_normalized'].isna()]['previous_grade']
        # unique unclassified grades
        unclassified_grades = pd.concat([unclassified_new_grades, unclassified_previous_grades]).unique()
        
        for grade in unclassified_grades:
            if grade:
                classification = classify_grade_embedding_similarity(grade, ref_grade_list, grade_mapping, update=True)
                print(f"The grade '{grade}' is classified as: {classification[1]}, {classification[2]}")
        # Re-apply normalization after updating mapping 
        df['new_grade_normalized'] = df['new_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[0])
        df['previous_grade_normalized'] = df['previous_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[0])
        df['new_grade_value'] = df['new_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[1])
        df['previous_grade_value'] = df['previous_grade'].apply(lambda x: grade_mapping.get(x, (None, None, None, None))[1])
    def get_action(row):
        if row['previous_grade_value'] is not None:
            if row['new_grade_value'] < row['previous_grade_value']:
                return 'upgrade'
            elif row['new_grade_value'] > row['previous_grade_value']:
                return 'downgrade'
            else:
                return 'reiterate'
        else:
            return 'initialize'
        return None
    
    df['action_normalized'] = df.apply(get_action, axis=1)
    df.drop(columns=['new_grade', 'previous_grade', 'new_grade_normalized', 'previous_grade_normalized', 'action'], inplace=True)
    df.rename(columns={'action_normalized': 'action', 'new_grade_value': 'new_grade', 'previous_grade_value': 'previous_grade'}, inplace=True)

    return df


def load_records(transformed_df):
    """
    Loads the transformed income statements data into the core.analyst_grades table.

    Args:
        transformed_df (pd.DataFrame): Transformed DataFrame matching core.analyst_grades schema.
    """
    # Connect to the database
    with connect_to_db() as conn:
        # Insert records into core.analyst_grades
        total_records = insert_records(conn, transformed_df, 'core.analyst_grades', ['tic', 'url'])
        print(f"Total records inserted/updated in core.analyst_grades: {total_records}")


def main():
    """
    Main function to orchestrate the ETL process for analyst grades.
    """
    # Step 1: Read raw analyst grades data
    raw_df = read_records()

    # Step 2: Transform the data
    transformed_df = transform_records(raw_df)
    transformed_df = normalize_analyst_grades(transformed_df)

    # Step 3: Load the transformed data into core.news
    load_records(transformed_df)

if __name__ == "__main__":
    main()