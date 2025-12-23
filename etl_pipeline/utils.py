from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

import json
import hashlib
import pandas as pd
import os
import numpy as np
import re
import math
from decimal import Decimal

load_dotenv()

llm = ChatOpenAI(model=os.getenv("OPENAI_LLM_MODEL"))

def run_llm(messages: list[BaseMessage]) -> dict:
    """Interact with the LLM using a system message and a human prompt."""
    try:
        response = llm.invoke(messages)
        return response
    except Exception as e:
        # Raise an exception to be handled by the graph or caller
        raise RuntimeError(f"LLM invocation failed: {e}")




def hash_dict(obj: dict) -> str:
    """
    Compute a stable SHA-256 hash of a JSON-like Python object.

    - sort_keys=True ensures consistent key order
    - separators=(',', ':') removes whitespace
    - ensure_ascii=False allows UTF-8 text to hash consistently
    """
    canonical_str = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

def hash_text(text: str) -> str:
    """
    Compute SHA-256 hash of a text string.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()



def _is_na(x) -> bool:
    # Robust NA/NaN detection across float, numpy, pandas
    if x is None:
        return True
    if isinstance(x, Decimal):
        return x.is_nan()
    if isinstance(x, float):
        return math.isnan(x)
    if isinstance(x, np.floating):
        return np.isnan(x)
    if pd is not None:
        try:
            return bool(pd.isna(x))
        except Exception:
            return False
    return False

def _json_sanitize(x):
    if _is_na(x):
        return None
    if isinstance(x, dict):
        return {k: _json_sanitize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_sanitize(v) for v in x]
    if isinstance(x, Decimal):
        return float(x)  # use str(x) instead if you need exact precision
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        # re-check after cast (in case it was nan-like)
        y = float(x)
        return None if _is_na(y) else y
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x



    
def none_if_empty(val):
    return None if val == "" else val



def timestamp_to_trading_date(timestamp):
    """
    Convert a timestamp to its corresponding trading date with a market-open cutoff.

    If the timestamp is before U.S. market open (09:30 America/New_York), the event
    is attributed to the previous calendar day; otherwise it uses the same day.
    This is useful to align after-hours/weekend analyst notes to the session they
    effectively inform.

    Args:
        timestamp (str | pd.Timestamp | datetime): Datetime-like object. Assumed to
            already represent America/New_York local time (or a naive time treated
            as such).

    Returns:
        datetime.date: The trading date to attribute the event to.

    Notes:
        - This is a simple cutoff rule; it does not skip market holidays/weekends.
          If you need true exchange-trading-day logic, apply a trading calendar
          mapping after this step.
        - Cutoff is 09:30 (inclusive of 09:30 → same-day; earlier → previous day).
    """
    timestamp = pd.to_datetime(timestamp)
    if timestamp.hour < 9 or (timestamp.hour == 9 and timestamp.minute < 30):
        timestamp -= pd.Timedelta(days=1)
    return timestamp.date()


def convert_numpy_types(record):
    # Convert numpy integer and float types in a dictionary to native Python types
    return {key: (None if value is None or (isinstance(value, float) and np.isnan(value)) else
                  int(value) if isinstance(value, np.integer) else
                  float(value) if isinstance(value, np.floating) else
                  value)
            for key, value in record.items()}


def calculate_streak(series: pd.Series, on_value=1) -> pd.Series:
    """
    Vectorized run-length of consecutive `on_value` up to each row.
    Example 1: [1,1,0,1,1,1] -> [1,2,0,1,2,3]
    Example 2: [1,1,0,1,1, NaN] -> [1,2,0,1,2,NaN]
    NaN is treated as not-on.
    """
    # s = series.eq(on_value).astype('Int64')
    # out = s.groupby((s != on_value).cumsum()).cumcount() + 1
    # # Ensure zero remains 0, but NaN stays as NaN
    # out = out.where(~s.isna(), np.nan).where(s.astype(bool), 0)
    # return out
    s = series.eq(on_value).fillna(False)
    # group by breaks where s == 0, then cumulative count within each group
    out = s.groupby((s == 0).cumsum()).cumsum()
    # ensure zeros where the flag is off
    out = out.where((s > 0) | (s.isna()), 0)
    out[series.isna()] = np.nan  # preserve NaNs from original series
    return out


def calculate_streak_pos_neg(series: pd.Series) -> pd.Series:
    """
    Vectorized run-length of consecutive `on_value` up to each row.
    Example: [1,1,0,0,1,1,1] -> [1,2,-1,-2,1,2,3]
    NaN is treated as not-on.
    """
    s = series.fillna(0).astype(int)
    pos_streak = s.eq(1).groupby((s != 1).cumsum()).cumcount() + 1
    neg_streak = s.eq(0).groupby((s != 0).cumsum()).cumcount() + 1
    out = pos_streak.where(s.eq(1), -neg_streak)
    return out


def calculate_capped_rate(current: float, previous: float) -> float:
    if previous is None or current is None:
        return None
    
    rate_change = (current - previous) / max(abs(previous), 1e-6)

    # Cap the rate change within ±1000%
    return max(min(rate_change, 10.0), -10.0)




def parse_json_from_llm(response_text):
    # Pattern to find a JSON object { ... }
    # re.DOTALL makes . match newlines as well
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return {}
    else:
        print("No JSON object found in response.")
        return {}
    


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
    if calendar_month in [4, 5, 6]:
        calendar_quarter = 1
    elif calendar_month in [7, 8, 9]:
        calendar_quarter = 2
    elif calendar_month in [10, 11, 12]:
        calendar_quarter = 3
    elif calendar_month in [1, 2, 3]:
        calendar_quarter = 4
        calendar_year -= 1
    return calendar_year, calendar_quarter


def get_fiscal_year_quarter(date):
    """
    Given a date, returns the corresponding fiscal year and quarter.

    Args:
        date (str or pd.Timestamp): The date.
    Returns:
        tuple: (fiscal_year, fiscal_quarter)
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)

    fiscal_year = date.year
    fiscal_month = date.month
    if fiscal_month in [1, 2, 3]:
        fiscal_quarter = 1
    elif fiscal_month in [4, 5, 6]:
        fiscal_quarter = 2
    elif fiscal_month in [7, 8, 9]:
        fiscal_quarter = 3
    elif fiscal_month in [10, 11, 12]:
        fiscal_quarter = 4

    return fiscal_year, fiscal_quarter

def filter_complete_years(df, tic, date_col='earnings_date', year_col=None, quarter_col=None):
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
    if date_col:
        df['year'] = pd.to_datetime(df[date_col]).dt.year
        df['quarter'] = pd.to_datetime(df[date_col]).dt.quarter
    if year_col and quarter_col:
        df['year'] = df[year_col]
        df['quarter'] = df[quarter_col]
    # Group by year and distinct count quarters
    earnings_per_year = df.groupby('year')['quarter'].nunique()
    earnings_per_year = earnings_per_year.sort_index(ascending=False)
    # Check if any year has not exactly 4 earnings except the most latest year
    latest_year = earnings_per_year.index.max()
    earliest_year = earnings_per_year.index.min()

    for year, count in earnings_per_year.items():
        if (year != latest_year and count == 4):
            years.append(year)
            continue
        elif (year == latest_year and 1 <= count <= 4):
            quarters = df[df['year'] == latest_year]['quarter'].to_list()
            if set(quarters) == set(list(range(1, count + 1))):
                years.append(year)
                continue
        elif (year == earliest_year and 1 <= count <= 4):
            quarters = df[df['year'] == earliest_year]['quarter'].to_list()
            if set(quarters) == set(list(range(5 - count, 5))):
                years.append(year)
                continue
        else:
            print(f"{tic} - Year {year} has {count} earnings records, expected 4.")
            break

    df = df[df['year'].isin(years)]
    df.drop(columns=['year', 'quarter'], inplace=True)
    return df


# def filter_complete_years(df, tic, date_col='earnings_date'):
#     """
#     Filters the earnings DataFrame to only include complete years (4 earnings per year),
#     except for the most recent year which can have up to 4 earnings.   
#     Args:
#         df (pd.DataFrame): DataFrame containing earnings data.
#     Returns:
#         pd.DataFrame: Filtered DataFrame with complete years only.
#     """
#     years = []
#     df = df.copy()
#     df['year'] = pd.to_datetime(df[date_col]).dt.year
#     # Group by year and count the number of earnings per year
#     earnings_per_year = df.groupby('year').size()
#     earnings_per_year = earnings_per_year.sort_index(ascending=False)
#     # Check if any year has not exactly 4 earnings except the most latest year
#     latest_year = earnings_per_year.index.max()
#     earliest_year = earnings_per_year.index.min()
#     for year, count in earnings_per_year.items():
#         if (year != latest_year and count == 4)\
#             or (year == latest_year and count <= 4):
#             years.append(year)
#         else:
#             print(f"{tic} - Year {year} has {count} earnings records, expected 4.")
#             break

#     df = df[df['year'].isin(years)]
#     df.drop(columns=['year'], inplace=True)
#     return df


def convert_decimals_to_float(df):
    """
    Iterates through a DataFrame and converts columns containing 
    decimal.Decimal objects into standard float types.
    """
    # Create a copy to avoid SettingWithCopy warnings on the original df
    df = df.copy()
    
    # Iterate only through 'object' columns where Decimals usually hide
    for col in df.select_dtypes(include=['object']).columns:
        
        # We check the first non-null value to see if it is a Decimal
        # (This is more efficient than checking every row)
        sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        
        if isinstance(sample_val, Decimal):
            # Efficiently convert the whole column
            df[col] = df[col].astype(float)
            
    return df