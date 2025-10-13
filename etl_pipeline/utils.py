from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

import json
import hashlib
import pandas as pd

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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