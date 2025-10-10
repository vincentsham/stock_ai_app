from __future__ import annotations
from enum import IntEnum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint
from prompts import PAST_PERFORMANCE_QUERIES, FUTURE_OUTLOOK_QUERIES, RISK_FACTORS_QUERIES

# ---- Enums / Literals ----
class Tri(IntEnum):
    NEG = -1
    NEU = 0
    POS = 1

class Horizon(IntEnum):
    SHORT = 0
    MID = 1
    LONG = 2

Binary01 = conint(ge=0, le=1)  # 0 or 1




# ---- Aspect States ----
class CompanyInfo(BaseModel):
    """
    Basic company and earnings information.
    """
    tic: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    company_description: Optional[str] = None
    fiscal_year: int
    fiscal_quarter: int
    earnings_date: Optional[str] = None

class RetrieverState(BaseModel):
    """
    State for retrieving relevant chunks.

    Input:
    - top_k: number of top chunks to retrieve
    - query_texts: list of query strings to guide retrieval

    Output:
    - chunks: list of retrieved transcript chunks
    - chunks_score: list of scores corresponding to the chunks
    """
    top_k: Optional[int] = 5  # Number of top chunks to retrieve
    queries: List[str] = Field(default_factory=list, description="List of query strings to guide retrieval")
    chunks: List[str] = Field(default_factory=list, description="List of relevant transcript chunks")
    chunks_score : List[float] = Field(default_factory=list, description="List of scores corresponding to the chunks")


class PastState(BaseModel):
    """
    State for analyzing past performance.

    Output (strict JSON):
    {
        "sentiment": -1|0|1,
        "durability": 0|1|2,
        "performance_factors": ["<factor1>", "<factor2>", ...],
        "summary": "<short summary with quotes>"
    }
    """
    sentiment: Optional[Tri] = None
    durability: Optional[Horizon] = None
    performance_factors: List[str] = []
    summary: Optional[str] = None

    

class FutureState(BaseModel):
    """
    State for analyzing future outlook.

    Output (strict JSON):
    {
        "guidance_direction": -1|0|1,
        "revenue_outlook": -1|0|1,
        "earnings_outlook": -1|0|1,
        "margin_outlook": -1|0|1,
        "cashflow_outlook": -1|0|1,
        "growth_acceleration": -1|0|1,
        "future_outlook_sentiment": -1|0|1,
        "catalysts": ["<factor1>", "<factor2>", ...],
        "summary": "<short factual summary with quotes>"
    }
    """
    guidance_direction: Optional[Tri] = None
    revenue_outlook: Optional[Tri] = None
    earnings_outlook: Optional[Tri] = None
    margin_outlook: Optional[Tri] = None
    cashflow_outlook: Optional[Tri] = None
    growth_acceleration: Optional[Tri] = None
    future_outlook_sentiment: Optional[Tri] = None
    catalysts: List[str] = []
    summary: Optional[str] = None



class RiskState(BaseModel):
    """
    State for analyzing risks.

    Output Format (strict JSON):
    {
        "risk_mentioned": 0|1,
        "risk_impact": -1|0|1,
        "risk_time_horizon": 0|1|2,
        "risk_factors": ["<factor1>", "<factor2>", ...],
        "summary": "<2–3 concise sentences with quotes>"
    }
    """
    risk_mentioned: Optional[Binary01] = None
    risk_impact: Optional[Tri] = None
    risk_time_horizon: Optional[Horizon] = None
    risk_factors: List[str] = []
    summary: Optional[str] = None


class RiskResponseState(BaseModel):
    """
    State for analyzing risk responses.

    Output (strict JSON only):
    {
    "mitigation_mentioned": 0|1,
    "mitigation_effectiveness": -1|0|1,
    "mitigation_time_horizon": 0|1|2,
    "mitigation_actions": ["<action1>", "<action2>", ...],
    "summary": "<2–3 concise sentences with quotes>"
    }
    """
    mitigation_mentioned: Optional[Binary01] = None
    mitigation_effectiveness: Optional[Tri] = None
    mitigation_time_horizon: Optional[Horizon] = None
    mitigation_actions: List[str] = []
    summary: Optional[str] = None


class MergedState(BaseModel):
    """
    Merged state combining PastState, FutureState, and RiskState.
    """
    company_info: CompanyInfo

    past_retriever: Optional[RetrieverState] = None
    future_retriever: Optional[RetrieverState] = None
    risk_retriever: Optional[RetrieverState] = None
    risk_response_retriever: Optional[RetrieverState] = None

    past_analysis: Optional[PastState] = None
    future_analysis: Optional[FutureState] = None
    risk_analysis: Optional[RiskState] = None
    risk_response_analysis: Optional[RiskResponseState] = None


def merged_state_factory(
        tic: str,
        company_name: Optional[str],
        industry: Optional[str],
        sector: Optional[str],
        company_description: Optional[str],
        fiscal_year: int,
        fiscal_quarter: int,
        earnings_date: Optional[str],
        top_k: int = 5,
) -> MergedState:
    """
    Helper function to create a MergedState object from company info and analysis states.
    """
    company_info = CompanyInfo(
        tic=tic,
        company_name=company_name,
        industry=industry,
        sector=sector,
        company_description=company_description,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        earnings_date=earnings_date
    )
    past_retriever_state = RetrieverState(top_k=top_k)
    past_retriever_state.queries = PAST_PERFORMANCE_QUERIES
    future_retriever_state = RetrieverState(top_k=top_k)
    future_retriever_state.queries = FUTURE_OUTLOOK_QUERIES
    risk_retriever_state = RetrieverState(top_k=top_k)
    risk_retriever_state.queries = RISK_FACTORS_QUERIES
    risk_response_retriever_state = RetrieverState(top_k=top_k)

    past_state = PastState()
    future_state = FutureState()
    risk_state = RiskState()
    risk_response_state = RiskResponseState()

    merged_state = MergedState(
        company_info=company_info,
        past_retriever=past_retriever_state,
        future_retriever=future_retriever_state,
        risk_retriever=risk_retriever_state,
        risk_response_retriever=risk_response_retriever_state,
        past_analysis=past_state,
        future_analysis=future_state,
        risk_analysis=risk_state,
        risk_response_analysis=risk_response_state
    )

    return merged_state
