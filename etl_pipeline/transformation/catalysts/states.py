from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import IntEnum

# ---- Literals (enums-as-strings) ----
CatalystType = Literal[
    "guidance_outlook", "product_initiative", "partnership_deal",
    "cost_efficiency", "capital_actions", "regulatory_policy",
    "demand_trends", "risk_event", "macro_policy",
]
# lifecycle for a single catalyst
LifecycleState = Literal["announced", "updated", "withdrawn", "realized"]

CertaintyLevel = Literal["confirmed", "planned", "rumor", "denied"]
SourceType = Literal["news", "earnings_transcript"]

ImpactArea = Literal[
    # --- Financial Performance ---
    "revenue", "earnings", "margin", "profitability", "cashflow", "expenses", "capex",
    # --- Operations & Execution ---
    "operations", "supply_chain", "capacity", "productivity", "headcount", "technology",
    # --- Strategic & Growth Drivers ---
    "strategy", "market_expansion", "demand", "volume", "pricing", "channel", "inventory",
    # --- Financial Structure & Capital Actions ---
    "shareholder_return", "financing", "balance_sheet", "leverage", "liquidity", "financial",
    # --- Regulatory, Legal, & Governance ---
    "compliance", "regulatory", "legal", "governance", "policy", "licensing", "risk",
    # --- Macro & External Environment ---
    "macro", "monetary_policy", "fiscal_policy", "trade_policy",
    "currency_fx", "commodity_prices", "inflation_cost", "geopolitical", "region",
    # --- ESG, Cyber, & Leadership ---
    "cybersecurity", "reputation", "leadership", "environmental",
]

# ---- Enums ----
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


# ---- Core catalyst payload ----
class Catalyst(BaseModel):
    # Stage 1
    is_catalyst: Optional[Binary] = Field(
        None, description="Indicates if the chunk is a catalyst for the given type"
    )
    rationale: Optional[str] = Field(
        None, description="Why the model decided this chunk is/is not a catalyst"
    )

    # optionally carry type forward
    catalyst_type: Optional[CatalystType] = Field(
        None, description="Catalyst type, typically copied from the ChunkContext"
    )

    # Stage 2
    catalyst_id: Optional[str] = Field(
        None, description="Unique identifier for the catalyst (existing if update)"
    )
    state: Optional[LifecycleState] = Field(
        None, description="Lifecycle/category of the catalyst"
    )
    title: Optional[str] = Field(
        None, description="Title of the catalyst event"
    )
    summary: Optional[str] = Field(
        None, description="Summary of the catalyst event"
    )
    evidence: Optional[str] = Field(
        None, description="Supporting evidence for the catalyst"
    )
    time_horizon: Optional[TimeHorizon] = Field(
        None, description="Time horizon for the catalyst impact"
    )
    certainty: Optional[CertaintyLevel] = Field(
        None, description="Certainty level of the catalyst impact"
    )
    impact_area: Optional[ImpactArea] = Field(
        None, description="Area affected by the catalyst"
    )
    sentiment: Optional[Tri] = Field(
        None, description="Sentiment of the catalyst"
    )
    impact_magnitude: Optional[Tri] = Field(
        None, description="Magnitude of the catalyst impact"
    )

    @classmethod
    def init(cls) -> "Catalyst":
        return cls()

    @classmethod
    def create(
        cls,
        is_catalyst: Binary,
        rationale: str,
        catalyst_type: CatalystType,
        catalyst_id: Optional[str] = None,
        state: Optional[LifecycleState] = None,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        evidence: Optional[str] = None,
        time_horizon: Optional[TimeHorizon] = None,
        certainty: Optional[CertaintyLevel] = None,
        impact_area: Optional[ImpactArea] = None,
        sentiment: Optional[Tri] = None,
        impact_magnitude: Optional[Tri] = None,
    ) -> "Catalyst":
        return cls(
            is_catalyst=is_catalyst,
            rationale=rationale,
            catalyst_type=catalyst_type,
            catalyst_id=catalyst_id,
            state=state,
            title=title,
            summary=summary,
            evidence=evidence,
            time_horizon=time_horizon,
            certainty=certainty,
            impact_area=impact_area,
            sentiment=sentiment,
            impact_magnitude=impact_magnitude,
        )


# ---- Company info ----
class CompanyInfo(BaseModel):
    tic: str = Field(..., description="Stock ticker symbol, e.g., AAPL")
    company_name: str = Field(..., description="Full company name, e.g., Apple Inc.")
    industry: str = Field(..., description="Industry of the company, e.g., Technology")
    sector: str = Field(..., description="Sector of the company, e.g., Consumer Electronics")
    company_description: str = Field(..., description="Description of the company")

    @classmethod
    def create(
        cls,
        tic: str,
        company_name: str,
        industry: str,
        sector: str,
        company_description: str,
    ) -> "CompanyInfo":
        return cls(
            tic=tic,
            company_name=company_name,
            industry=industry,
            sector=sector,
            company_description=company_description,
        )


# ---- Query params for retrieval ----
class QueryParameters(BaseModel):
    tic: str = Field(..., description="Stock ticker symbol, e.g., AAPL")
    calendar_year: int = Field(..., description="Calendar year of the earnings/transcript")
    calendar_quarter: Optional[int] = Field(None, description="Calendar quarter of the earnings/transcript")
    calendar_month: Optional[int] = Field(None, description="Calendar month of the news article")
    source_type: SourceType = Field(..., description="Source of the news/earnings transcript")
    catalyst_type: CatalystType = Field(..., description="Type of catalyst event to evaluate")
    top_k: int = Field(3, description="Number of top similar chunks to retrieve")


# ---- One retrieved chunk ----
class ChunkContext(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the earnings/transcript event")
    chunk_id: int = Field(..., description="Unique identifier for the chunk within the event")
    source_type: SourceType = Field(..., description="Source of the news/earnings transcript")
    catalyst_type: CatalystType = Field(..., description="Type of catalyst event to evaluate")
    retrieval_query: str = Field(..., description="RAG query used to retrieve this chunk")
    date: str = Field(..., description="Date of the earnings/transcript/news")
    content: str = Field(..., description="Actual transcript/news chunk to classify")
    score: float = Field(..., description="Cosine similarity score for the chunk")
    source: str = Field(..., description="Source of the chunk, e.g., news URL or transcript ID")
    url: Optional[str] = Field(None, description="URL of the news article, if applicable")
    raw_json_sha256: str = Field(..., description="SHA-256 hash of the raw JSON payload")



# ---- One catalyst + the chunk that produced it ----
class CatalystContext(BaseModel):
    chunk: ChunkContext = Field(..., description="The chunk to analyze for catalyst detection")
    candidate: Catalyst = Field(..., description="Stage-2 result: normalized catalyst built from this chunk")

    @classmethod
    def create_from_chunk(cls, 
                   event_id: str,
                   chunk_id: int,
                   source_type: SourceType, 
                   catalyst_type: CatalystType, 
                   retrieval_query: str, 
                   date: str, 
                   content: str,  
                   score: float,
                   source: str,
                   url: str,
                   raw_json_sha256: str
                   ) -> "CatalystContext":
        chunk = ChunkContext(
            event_id=event_id,
            chunk_id=chunk_id,
            source_type=source_type,
            catalyst_type=catalyst_type,
            retrieval_query=retrieval_query,
            date=date,
            content=content,
            score=score,
            source=source,
            url=url,
            raw_json_sha256=raw_json_sha256,
        )
        return cls(chunk=chunk, candidate=Catalyst.init())


# ---- Top-level run/session state ----
class CatalystSession(BaseModel):
    company_info: CompanyInfo = Field(..., description="Basic company information")
    query_params: QueryParameters = Field(..., description="Parameters used for chunk retrieval")
    current_catalysts: List[Catalyst] = Field(
        default_factory=list,
        description="Existing catalysts for THIS company and THIS catalyst_type (for update matching)",
    )
    catalysts: List[CatalystContext] = Field(
        default_factory=list,
        description="All catalysts detected from the chunks for this company",
    )


# ---- Factory ----
def catalyst_session_factory(
    tic: str,
    company_name: str,
    industry: str,
    sector: str,
    company_description: str,
    source_type: SourceType,
    catalyst_type: CatalystType,
    calendar_year: int,
    calendar_quarter: Optional[int] = None,
    calendar_month: Optional[int] = None,
    top_k: int = 3,
) -> CatalystSession:
    company_info = CompanyInfo.create(
        tic=tic,
        company_name=company_name,
        industry=industry,
        sector=sector,
        company_description=company_description,
    )

    query_params = QueryParameters(
        tic=tic,
        calendar_year=calendar_year,
        calendar_quarter=calendar_quarter,
        calendar_month=calendar_month,
        source_type=source_type,
        catalyst_type=catalyst_type,
        top_k=top_k,
    )

    return CatalystSession(
        company_info=company_info,
        query_params=query_params,
    )