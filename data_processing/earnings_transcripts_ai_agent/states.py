from __future__ import annotations
from enum import IntEnum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint

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

class RetrieverState(CompanyInfo):
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

    @classmethod
    def from_parent(cls, parent: CompanyInfo, **kwargs) -> RetrieverState:
        return cls(**parent.model_dump(), **kwargs)

class PastState(RetrieverState):
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

    @classmethod
    def from_parent(cls, parent: RetrieverState, **kwargs) -> PastState:
        return cls(**parent.model_dump(), **kwargs)
    

class FutureState(RetrieverState):
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

    @classmethod
    def from_parent(cls, parent: RetrieverState, **kwargs) -> FutureState:
        return cls(**parent.model_dump(), **kwargs)


class RiskState(RetrieverState):
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

    @classmethod
    def from_parent(cls, parent: RetrieverState, **kwargs) -> RiskState:
        return cls(**parent.model_dump(), **kwargs)


class MergedState(BaseModel):
    """
    Merged state combining PastState, FutureState, and RiskState.
    """
    company_info: CompanyInfo
    past: Optional[PastState] = None
    future: Optional[FutureState] = None
    risk: Optional[RiskState] = None

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
    past_retriever = RetrieverState.from_parent(
        parent=company_info,
        top_k=top_k
    )
    
    future_retriever = RetrieverState.from_parent(
        parent=company_info,
        top_k=top_k
    )
    risk_retriever = RetrieverState.from_parent(
        parent=company_info,
        top_k=top_k
    )

    past_state = PastState.from_parent(parent=past_retriever)
    future_state = FutureState.from_parent(parent=future_retriever)
    risk_state = RiskState.from_parent(parent=risk_retriever)

    merged_state = MergedState(
        company_info=company_info,
        past=past_state,
        future=future_state,
        risk=risk_state
    )
    return merged_state
