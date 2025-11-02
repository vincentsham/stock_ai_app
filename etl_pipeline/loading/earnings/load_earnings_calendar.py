import pandas as pd
import json
from server.database.utils import connect_to_db, insert_records, execute_query
from functools import partial

def read_earnings_records(tic):
    """
    Reads data from the raw.earnings table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT 
        tic,
        earnings_date,
        fiscal_date,
        session
    FROM raw.earnings 
    WHERE tic = '{tic}'
    ORDER BY earnings_date DESC;
    """
    # Connect to the database
    df = execute_query(query)
    return df

def filter_complete_years(df, tic):
    """
    Filters the earnings DataFrame to only include complete years (4 earnings per year),
    except for the most recent year which can have up to 4 earnings.   
    Args:
        df (pd.DataFrame): DataFrame containing earnings data.
    Returns:
        pd.DataFrame: Filtered DataFrame with complete years only.
    """
    years = []
    df = df.copy()
    df['year'] = pd.to_datetime(df['earnings_date']).dt.year
    # Group by year and count the number of earnings per year
    earnings_per_year = df.groupby('year').size()
    earnings_per_year = earnings_per_year.sort_index(ascending=False)
    # Check if any year has not exactly 4 earnings except the most latest year
    latest_year = earnings_per_year.index.max()
    earliest_year = earnings_per_year.index.min()
    for year, count in earnings_per_year.items():
        if (year != latest_year and count == 4)\
            or (year == latest_year and count <= 4)\
            or (year == earliest_year and count <= 4):
            years.append(year)
        else:
            print(f"{tic} - Year {year} has {count} earnings records, expected 4.")
            break

    df = df[df['year'].isin(years)]
    df.drop(columns=['year'], inplace=True)
    return df

def read_income_statements_records(tic):
    """
    Reads data from the raw.income_statements table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT 
        tic,
        fiscal_year,
        fiscal_quarter,
        fiscal_date
    FROM raw.income_statements 
    WHERE tic = '{tic}' 
        AND fiscal_quarter != 0
    ORDER BY fiscal_date DESC;
    """
    # Connect to the database
    df = execute_query(query)
    return df


def fiscal_to_calendar(fiscal_year, fiscal_quarter, delta):
    """
    Converts fiscal year and quarter to calendar year and quarter based on a delta.

    Args:
        fiscal_year (int): The fiscal year.
        fiscal_quarter (int): The fiscal quarter (1-4).
        delta (int): The number of months to adjust from fiscal to calendar.

    Returns:
        tuple: (calendar_year, calendar_quarter)
    """
    # Calculate the month corresponding to the fiscal quarter
    fiscal_month = (fiscal_quarter - 1) * 3 + 1  # 1, 4, 7, 10

    # Adjust month by delta
    calendar_month = fiscal_month + delta
    calendar_year = fiscal_year

    # Handle year rollover
    if calendar_month > 12:
        calendar_month -= 12
        calendar_year += 1
    elif calendar_month < 1:
        calendar_month += 12
        calendar_year -= 1

    # Determine calendar quarter
    if calendar_month in [1, 2, 3]:
        calendar_quarter = 1
    elif calendar_month in [4, 5, 6]:
        calendar_quarter = 2
    elif calendar_month in [7, 8, 9]:
        calendar_quarter = 3
    else:
        calendar_quarter = 4

    return calendar_year, calendar_quarter


def get_calendar_year_quarter_fn(tic):

    query = f"""
        SELECT l.earnings_date, r.fiscal_year, r.fiscal_quarter
        FROM raw.earnings AS l 
        INNER JOIN raw.income_statements AS r
        ON l.tic = r.tic AND ABS(l.fiscal_date::DATE - r.fiscal_date::DATE) < 15
        WHERE l.tic = '{tic}'
        ORDER BY earnings_date DESC
        LIMIT 1;
    """
    # Connect to the database
    df = execute_query(query)
    if df.empty:
        raise ValueError(f"No earnings or income statement records found for TIC: {tic}")
    earnings_date = pd.to_datetime(df['earnings_date'].iloc[0])
    calendar_year = earnings_date.year
    calendar_month = earnings_date.month    
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

    delta = calendar_year + calendar_quarter/4 - (df['fiscal_year'].iloc[0] + df['fiscal_quarter'].iloc[0]/4)
    delta_months = round(delta * 12)
    
    return partial(fiscal_to_calendar, delta=delta_months)


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

# def transform_earnings_records(tic):
#     """
#     Transforms the raw earnings data to match the schema of core.earnings.
    
#     Args:
#         raw_df (pd.DataFrame): DataFrame containing raw earnings data.
#     Returns:
#         pd.DataFrame: Transformed DataFrame matching core.earnings schema.
#     """
    
#     earnings_df = read_earnings_records(tic)
#     output = {"tic": [], "calendar_year": [], "calendar_quarter": [], 
#               "earnings_date": [], "fiscal_date": [], "session": []}
#     calendar_year, calendar_quarter = get_calendar_year_quarter(earnings_df['earnings_date'].iloc[0])

#     for i in range(len(earnings_df)):
#         _calendar_year, _calendar_quarter = get_calendar_year_quarter(earnings_df['earnings_date'].iloc[i])
#         if _calendar_year != calendar_year or _calendar_quarter != calendar_quarter:
#             print(f"{tic} - Mismatch in calculated calendar year/quarter for earnings date {earnings_df['earnings_date'].iloc[i]}: "
#                   f"{_calendar_year}/{_calendar_quarter} vs {calendar_year}/{calendar_quarter}")
#             break
#         output['tic'].append(tic)
#         output['calendar_year'].append(calendar_year)
#         output['calendar_quarter'].append(calendar_quarter)
#         output['earnings_date'].append(pd.to_datetime(earnings_df['earnings_date'].iloc[i]))
#         output['fiscal_date'].append(pd.to_datetime(earnings_df['fiscal_date'].iloc[i]))
#         output['session'].append(earnings_df['session'].iloc[i])

#         calendar_quarter -= 1
#         if calendar_quarter < 1:
#             calendar_quarter = 4
#             calendar_year -= 1

#     output = pd.DataFrame(output)
#     output['fiscal_year'], output['fiscal_quarter'] = None, None
#     return output


def transform_earnings_records(tic):
    """
    Transforms the raw earnings data to match the schema of core.earnings.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw earnings data.
    Returns:
        pd.DataFrame: Transformed DataFrame matching core.earnings schema.
    """
    print(f"Transforming earnings records for {tic}...")
    earnings_df = read_earnings_records(tic)
    earnings_df = filter_complete_years(earnings_df, tic)

    output = {"tic": [], "calendar_year": [], "calendar_quarter": [], 
              "earnings_date": [], "fiscal_date": [], "session": []}
    
    earnings_df = earnings_df.sort_values(by='earnings_date', ascending=False).reset_index(drop=True)
    calendar_year, calendar_quarter = get_calendar_year_quarter(earnings_df['earnings_date'].iloc[0])
    
    for i in range(len(earnings_df)):
        output['tic'].append(tic)
        output['calendar_year'].append(calendar_year)
        output['calendar_quarter'].append(calendar_quarter)
        output['earnings_date'].append(pd.to_datetime(earnings_df['earnings_date'].iloc[i]))
        output['fiscal_date'].append(pd.to_datetime(earnings_df['fiscal_date'].iloc[i]))
        output['session'].append(earnings_df['session'].iloc[i])

        calendar_quarter -= 1
        if calendar_quarter < 1:
            calendar_quarter = 4
            calendar_year -= 1

    output = pd.DataFrame(output)
    output['fiscal_year'], output['fiscal_quarter'] = None, None
    return output


def transform_income_statements_records(tic):
    """
    Transforms the raw income statements data to match the schema of core.earnings.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw income statements data.
    Returns:
        pd.DataFrame: Transformed DataFrame matching core.earnings schema.
    """
    income_statements_df = read_income_statements_records(tic)
    income_statements_df = income_statements_df.sort_values(by=['fiscal_year', 'fiscal_quarter'], 
                                                            ascending=[False, False]).reset_index(drop=True)   
    fiscal_to_calendar_fn = get_calendar_year_quarter_fn(tic)
    income_statements_df['calendar_year'], income_statements_df['calendar_quarter'] \
        = zip(*income_statements_df.apply(
            lambda row: fiscal_to_calendar_fn(row['fiscal_year'], row['fiscal_quarter']),
            axis=1
        ))

    return income_statements_df





def transform_records(tic):
    """
    Transforms the raw earnings data to match the schema of core.earnings.
    
    Args:
        raw_df (pd.DataFrame): DataFrame containing raw earnings data.
    Returns:
        pd.DataFrame: Transformed DataFrame matching core.earnings schema.
    """

    earnings_df = transform_earnings_records(tic)

    income_statements_df = transform_income_statements_records(tic)

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
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        records = cursor.fetchall()
        for record in records:
            tic = record[0]
            df = transform_records(tic)
            total_records = load_records(df)
            print(f"For {tic}: Total records processed = {total_records}")
        conn.close()



if __name__ == "__main__":
    main()