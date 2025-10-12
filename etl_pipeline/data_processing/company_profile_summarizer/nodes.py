from states import CompanyProfileState
from prompts import SYSTEM_PROMPT, HUMAN_PROMPT
from data_processing.utils import run_llm  # Adjust import if needed
import json


def summarize_company_profile(state: CompanyProfileState) -> dict:
    """
    Calls LLM to generate both summary and short_summary for a company profile.
    Fills the output fields in the state and returns it.
    """
    # Prepare the prompt
    system_prompt = SYSTEM_PROMPT
    human_prompt = HUMAN_PROMPT.format(
        tic=state.tic,
        company_name=state.company_name or "",
        sector=state.sector or "",
        industry=state.industry or "",
        country=state.country or "",
        market_cap=state.market_cap or "",
        employees=state.employees or "",
        exchange=state.exchange or "",
        currency=state.currency or "",
        website=state.website or "",
        description=state.description or ""
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": human_prompt}
    ]
    # Call the LLM (assume run_llm returns an object with .content)
    response = run_llm(messages)
    result = json.loads(response.content)
    summary = result.get("summary")
    short_summary = result.get("short_summary")
    return  {"summary": summary, "short_summary": short_summary}
