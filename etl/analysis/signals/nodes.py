from states import Signal
from prompts import SYSTEM_PROMPT, HUMAN_PROMPT
from etl.utils import run_llm, parse_json_from_llm  # Adjust import if needed
import json


def is_signal_node(state: Signal) -> dict:
    """
    Calls LLM to generate both summary and short_summary for a company profile.
    Fills the output fields in the state and returns it.
    """
    # Prepare the prompt
    system_prompt = SYSTEM_PROMPT.format(
        company_info=state.company_info
    )
    human_prompt = HUMAN_PROMPT.format(
        company_info=state.company_info,
        content=state.content
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": human_prompt}
    ]
    # Call the LLM (assume run_llm returns an object with .content)
    response = run_llm(messages)
    result = parse_json_from_llm(response.content)
    # print(result)
    # Extract values, defaulting to 'No Signal' if parsing is ambiguous
    is_signal_raw = result.get("is_signal", 0)
    reason = result.get("reason", "No reason provided")

    # We return a dict that LangGraph will merge into the Signal state.
    # Note: result.get("is_signal") will likely be an int (0 or 1), 
    # which Pydantic/Enum handles automatically.
    return {
        "is_signal": is_signal_raw, 
        "reason": reason
    }