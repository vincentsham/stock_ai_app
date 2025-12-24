from __future__ import annotations
from enum import IntEnum
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint
from prompts import PAST_PERFORMANCE_QUERIES, FUTURE_OUTLOOK_QUERIES, RISK_FACTORS_QUERIES

# ---- Enums / Literals ----
class Tri(IntEnum):
    NEG = -1
    NEU = 0
    POS = 1

class TimeHorizon(IntEnum):
    SHORT = 0
    MID = 1
    LONG = 2

class Binary(IntEnum):
    NO = 0
    YES = 1





# ---- Aspect States ----
class CompanyInfo(TypedDict):
    """
    Basic company and earnings information.
    """
    tic: str
    calendar_year: int
    calendar_quarter: int
    earnings_date: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    company_description: Optional[str] = None

    @classmethod
    def create(cls, 
               tic: str,
               calendar_year: int,
               calendar_quarter: int,
               earnings_date: Optional[str] = None,
               company_name: Optional[str] = None,
               industry: Optional[str] = None,
               sector: Optional[str] = None,
               company_description: Optional[str] = None) -> CompanyInfo:
        return cls(
            tic=tic,
            calendar_year=calendar_year,
            calendar_quarter=calendar_quarter,
            earnings_date=earnings_date,
            company_name=company_name,
            industry=industry,
            sector=sector,
            company_description=company_description
        )  

class RetrieverState(TypedDict):
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
    queries: List[str] = []
    chunks: List[str] = []
    chunks_score : List[float] = []

    @classmethod
    def create(cls, 
               top_k: int = 5,
               queries: List[str] = [],
               chunks: List[str] = [],
               chunks_score: List[float] = []) -> RetrieverState:
        return cls(
            top_k=top_k,
            queries=queries,
            chunks=chunks,
            chunks_score=chunks_score
        )

class PastState(BaseModel):
    """
    State for analyzing past performance.

    Output (strict JSON):
    {
        "sentiment": -1|0|1,
        "durability": 0|1|2,
        "performance_factors": ["<factor1>", "<factor2>", ...],
        "past_summary": "<short summary with quotes>"
    }
    """
    sentiment: Optional[Tri] = None
    durability: Optional[TimeHorizon] = None
    performance_factors: List[str] = []
    past_summary: Optional[str] = None

    @classmethod
    def create(cls,
               sentiment: Optional[Tri] = None,
               durability: Optional[TimeHorizon] = None,
               performance_factors: Optional[List[str]] = [],
               past_summary: Optional[str] = None) -> PastState:
        return cls(
            sentiment=sentiment,
            durability=durability,
            performance_factors=performance_factors,
            past_summary=past_summary
        )

class FutureState(TypedDict):
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
        "growth_drivers": ["<factor1>", "<factor2>", ...],
        "future_summary": "<short factual summary with quotes>"
    }
    """
    guidance_direction: Optional[Tri] = None
    revenue_outlook: Optional[Tri] = None
    earnings_outlook: Optional[Tri] = None
    margin_outlook: Optional[Tri] = None
    cashflow_outlook: Optional[Tri] = None
    growth_acceleration: Optional[Tri] = None
    future_outlook_sentiment: Optional[Tri] = None
    growth_drivers: List[str] = []
    future_summary: Optional[str] = None

    @classmethod
    def create(cls,
               guidance_direction: Optional[Tri] = None,
               revenue_outlook: Optional[Tri] = None,
               earnings_outlook: Optional[Tri] = None,
               margin_outlook: Optional[Tri] = None,
               cashflow_outlook: Optional[Tri] = None,
               growth_acceleration: Optional[Tri] = None,
               future_outlook_sentiment: Optional[Tri] = None,
               growth_drivers: List[str] = [],
               future_summary: Optional[str] = None) -> FutureState:
        return cls(
            guidance_direction=guidance_direction,
            revenue_outlook=revenue_outlook,
            earnings_outlook=earnings_outlook,
            margin_outlook=margin_outlook,
            cashflow_outlook=cashflow_outlook,
            growth_acceleration=growth_acceleration,
            future_outlook_sentiment=future_outlook_sentiment,
            growth_drivers=growth_drivers,
            future_summary=future_summary
        )



class RiskState(TypedDict):
    """
    State for analyzing risks.

    Output Format (strict JSON):
    {
        "risk_mentioned": 0|1,
        "risk_impact": -1|0|1,
        "risk_time_horizon": 0|1|2,
        "risk_factors": ["<factor1>", "<factor2>", ...],
        "risk_summary": "<2–3 concise sentences with quotes>"
    }
    """
    risk_mentioned: Optional[Binary] = None
    risk_impact: Optional[Tri] = None
    risk_time_horizon: Optional[TimeHorizon] = None
    risk_factors: List[str] = []
    risk_summary: Optional[str] = None

    @classmethod
    def create(cls,
               risk_mentioned: Optional[Binary] = None,
               risk_impact: Optional[Tri] = None,
               risk_time_horizon: Optional[TimeHorizon] = None,
               risk_factors: List[str] = [],
               risk_summary: Optional[str] = None) -> RiskState:
        return cls(
            risk_mentioned=risk_mentioned,
            risk_impact=risk_impact,
            risk_time_horizon=risk_time_horizon,
            risk_factors=risk_factors,
            risk_summary=risk_summary
        )


class RiskResponseState(TypedDict):
    """
    State for analyzing risk responses.

    Output (strict JSON only):
    {
    "mitigation_mentioned": 0|1,
    "mitigation_effectiveness": -1|0|1,
    "mitigation_time_horizon": 0|1|2,
    "mitigation_actions": ["<action1>", "<action2>", ...],
    "mitigation_summary": "<2–3 concise sentences with quotes>"
    }
    """
    mitigation_mentioned: Optional[Binary] = None
    mitigation_effectiveness: Optional[Tri] = None
    mitigation_time_horizon: Optional[TimeHorizon] = None
    mitigation_actions: List[str] = []
    mitigation_summary: Optional[str] = None

    @classmethod
    def create(cls,
               mitigation_mentioned: Optional[Binary] = None,
               mitigation_effectiveness: Optional[Tri] = None,
               mitigation_time_horizon: Optional[TimeHorizon] = None,
               mitigation_actions: List[str] = [],
               mitigation_summary: Optional[str] = None) -> RiskResponseState:
        return cls(
            mitigation_mentioned=mitigation_mentioned,
            mitigation_effectiveness=mitigation_effectiveness,
            mitigation_time_horizon=mitigation_time_horizon,
            mitigation_actions=mitigation_actions,
            mitigation_summary=mitigation_summary
        )


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
        calendar_year: int,
        calendar_quarter: int,
        earnings_date: Optional[str],
        top_k: int = 5,
) -> MergedState:
    """
    Helper function to create a MergedState object from company info and analysis states.
    """
    company_info = CompanyInfo.create(
        tic=tic,
        company_name=company_name,
        industry=industry,
        sector=sector,
        company_description=company_description,
        calendar_year=calendar_year,
        calendar_quarter=calendar_quarter,
        earnings_date=earnings_date
    )
    past_retriever_state = RetrieverState.create(top_k=top_k, queries=PAST_PERFORMANCE_QUERIES)
    future_retriever_state = RetrieverState.create(top_k=top_k, queries=FUTURE_OUTLOOK_QUERIES)
    risk_retriever_state = RetrieverState.create(top_k=top_k, queries=RISK_FACTORS_QUERIES)
    risk_response_retriever_state = RetrieverState.create(top_k=top_k)

    past_state = PastState.create()
    future_state = FutureState.create()
    risk_state = RiskState.create()
    risk_response_state = RiskResponseState.create()

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
