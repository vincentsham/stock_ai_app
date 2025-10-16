from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

import json
import hashlib
import pandas as pd
import os
import numpy as np

load_dotenv()

llm = ChatOpenAI(model=os.getenv("OPENAI_LLM_MODEL"), temperature=0)

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


def read_sql_query(query: str, conn) -> pd.DataFrame:
    """Execute a SQL query and return the results as a pandas DataFrame."""
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)
            return df
    except Exception as e:
        print(f"Error executing query: {e}")
        raise e
    
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