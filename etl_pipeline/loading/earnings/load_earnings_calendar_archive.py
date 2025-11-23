import pandas as pd
import json
from database.utils import connect_to_db, insert_records, execute_query


def read_earnings_records():
    """
    Reads data from the raw.earnings table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT 
        tic,
        earnings_date,
        fiscal_date,
        session
    FROM raw.earnings ORDER BY tic, earnings_date DESC;
    """

    # Connect to the database
    df = execute_query(query)
    return df

def read_income_statements_records():
    """
    Reads data from the raw.income_statements table and returns it as a pandas DataFrame.
    """
    query = """
    SELECT 
        tic,
        fiscal_year,
        fiscal_quarter,
        fiscal_date
    FROM raw.income_statements ORDER BY tic, fiscal_date DESC;
    """

    # Connect to the database
    df = execute_query(query)
    return df



def get_calendar_year_quarter(date):
    """
    Given a date, returns the corresponding calendar year and quarter.

    Args:
        date (str or pd.Timestamp): The date.
    Returns:
        tuple: (calendar_year, calendar_quarter)
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)

    calendar_year = date.year
    calendar_month = date.month
    if calendar_month in [3, 4, 5]:
        calendar_quarter = 1
    elif calendar_month in [6, 7, 8]:
        calendar_quarter = 2
    elif calendar_month in [9, 10, 11]:
        calendar_quarter = 3
    elif calendar_month in [12]:
        calendar_quarter = 4
    elif calendar_month in [1, 2]:
        calendar_quarter = 4
        calendar_year -= 1
    return calendar_year, calendar_quarter


def transform_records():
    """
    Transforms the raw earnings data to match the schema of core.earnings.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw earnings data.
    Returns:
        pd.DataFrame: Transformed DataFrame matching core.earnings schema.
    """

    earnings_df = read_earnings_records()

    earnings_df['calendar_year'], earnings_df['calendar_quarter'] = zip(*earnings_df['earnings_date'].apply(get_calendar_year_quarter))
    earnings_df['fiscal_year'], earnings_df['fiscal_quarter'] = None, None
    earnings_df = earnings_df[[
        'tic', 'calendar_year', 'calendar_quarter','earnings_date', 'fiscal_year', 'fiscal_quarter', 'fiscal_date', 'session'
    ]].copy()

    income_statements_df = read_income_statements_records()
    income_statements_df['calendar_year'], income_statements_df['calendar_quarter'] = zip(*income_statements_df['fiscal_date'].apply(get_calendar_year_quarter))
    income_statements_df = income_statements_df[[
        'tic', 'calendar_year', 'calendar_quarter', 'fiscal_year', 'fiscal_quarter', 'fiscal_date'
    ]].copy()

   # import pdb; pdb.set_trace()

    joined_df = pd.merge(
        earnings_df,
        income_statements_df,
        on=['tic', 'calendar_year', 'calendar_quarter'],
        how='left',
        suffixes=('', '_inc')
    )

    # import pdb; pdb.set_trace()
    transformed_df = joined_df[['tic', 'calendar_year', 'calendar_quarter', 'earnings_date',  'fiscal_year', 'fiscal_quarter', 'fiscal_date', 'session']].copy()
    transformed_df['fiscal_year'] = joined_df['fiscal_year_inc']
    transformed_df['fiscal_quarter'] = joined_df['fiscal_quarter_inc']
    # if joined_df['fiscal_date'] is None, then use joined_df['fiscal_date_inc']
    transformed_df['fiscal_date'] = joined_df.apply(
        lambda row: row['fiscal_date_inc'] if pd.notnull(row['fiscal_date_inc']) else row['fiscal_date'],
        axis=1
    )  

    return transformed_df

def load_records(transformed_df):
    """
    Loads the transformed earnings data into the core.earnings table.
    """
    # Insert the transformed records into the database
    with connect_to_db() as conn:
        total_inserted = insert_records(conn, transformed_df, "core.earnings_calendar", ["tic", "calendar_year", "calendar_quarter"])
        print(f"Total records inserted: {total_inserted}")

    # Close the database connection
    return total_inserted

def main():
    """
    Main function to orchestrate the ETL process for earnings.
    """
    transformed_df = transform_records()
    load_records(transformed_df)

if __name__ == "__main__":
    main()