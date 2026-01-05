import pandas as pd
import numpy as np
from database.utils import execute_query


def read_earnings_calendar(tic):
    """
    Reads data from the raw.earnings_calendar table and returns it as a pandas DataFrame.
    """
    query = f"""
    SELECT 
        tic,
        calendar_year,
        calendar_quarter,
        earnings_date,
        fiscal_year,
        fiscal_quarter,
        fiscal_date,
        session
    FROM core.earnings_calendar
    WHERE tic = '{tic}';
    """

    # Connect to the database
    df = execute_query(query)
    return df


def fuzzy_lookup_earnings_calendar(tic, df, calendar_df, cols):
    """
    Update the earnings_date in df based on a fuzzy match with calendar_df.
    The fuzzy match is based on abs(df['earnings_date'] - calendar_df['earnings_date']) < 30 days.
    """
    df['earnings_date'] = pd.to_datetime(df['earnings_date'])
    calendar_df['earnings_date'] = pd.to_datetime(calendar_df['earnings_date'])
    # Sort both dataframes by earnings_date for merge_asof
    df = df.sort_values('earnings_date')
    calendar_df = calendar_df.sort_values('earnings_date')
    calendar_df['_earnings_date'] = calendar_df['earnings_date']
    calendar_df['_fiscal_date'] = calendar_df['fiscal_date']
    calendar_df['_session'] = calendar_df['session']
    calendar_df['_calendar_year'] = calendar_df['calendar_year']
    calendar_df['_calendar_quarter'] = calendar_df['calendar_quarter']
    calendar_df['_fiscal_year'] = calendar_df['fiscal_year']
    calendar_df['_fiscal_quarter'] = calendar_df['fiscal_quarter']
    calendar_df['index'] = np.arange(len(calendar_df))

    # Perform an asof merge to find the nearest match within 30 days
    # We match on 'earnings_date' and group by 'tic' to ensure we only match the same stock
    merged_df = pd.merge_asof(
        df,
        calendar_df,
        on='earnings_date',
        by='tic',
        direction='nearest',
        tolerance=pd.Timedelta(days=20),
        suffixes=('', '_cal')
    )
    # if tic == 'AAPL':
    #     import pdb; pdb.set_trace()
    # import pdb; pdb.set_trace()
    # Update earnings_df with matched calendar data
    merged_df['calendar_year'] = merged_df['_calendar_year']
    merged_df['calendar_quarter'] = merged_df['_calendar_quarter']
    merged_df['earnings_date'] = merged_df['_earnings_date']
    merged_df['fiscal_year'] = merged_df['_fiscal_year']
    merged_df['fiscal_quarter'] = merged_df['_fiscal_quarter']
    merged_df['fiscal_date'] = merged_df['_fiscal_date']
    merged_df['session'] = merged_df['_session']

    # Drop rows where no match was found
    merged_df = merged_df.dropna(subset=['index'])
    merged_df = merged_df.sort_values('earnings_date', ascending=False)

    # Validate that there is no duplicate or missing matches after the merge
    if merged_df.shape[0] == 0:
        pass
    else:
        index = merged_df.iloc[0]['index']
        for i in range(1, len(merged_df)): 
            if merged_df.iloc[i]['index'] != index - 1:
                merged_df = merged_df.iloc[:i-1]
                break
            index = merged_df.iloc[i]['index']

    # check again whether there are any duplicates for col index
    if merged_df['index'].duplicated().any():
        raise ValueError(f"Duplicate matches found for tic {tic} after fuzzy lookup.")
    if merged_df['index'].isnull().any():
        raise ValueError(f"Missing matches found for tic {tic} after fuzzy lookup.")
    if len(merged_df) < 3:
        raise ValueError(f"Too few matches ({len(merged_df)}) found for tic {tic} after fuzzy lookup.")


    merged_df = merged_df[cols]
    return merged_df

