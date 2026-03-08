from typing import List, Dict, Optional, Literal, TypedDict, Annotated, Union
from pydantic import BaseModel, Field, field_validator, BeforeValidator
import operator
from datetime import date


def _coerce_str(v) -> str:
    return str(v)

CoercedStr = Annotated[str, BeforeValidator(_coerce_str)]

# Map common LLM mistakes to valid ImpactArea values
_IMPACT_AREA_ALIASES = {
    "ops & strategy": "operations",
    "ops and strategy": "operations",
    "market dynamics": "demand",
    "capital & risk": "risk",
    "capital and risk": "risk",
    "financials": "revenue",
    "external": "macro",
}

# Define explicit lambdas to satisfy the (a, b) -> c requirement
def add_reducer(a, b):
    return operator.add(a, b)

def set_reducer(a, b):
    return b  # Simply replaces the old value with the new one


# --- 1. Literal Definitions (Keeping your established types) ---
CatalystType = Literal[
    "guidance_outlook", "product_initiative", "partnership_deal", 
    "cost_efficiency", "capital_actions", "regulatory_policy", 
    "demand_trends", "risk_event", "macro_policy"
]

ImpactArea = Literal[
    "revenue", "earnings", "margin", "cashflow", "expenses", "capex",
    "operations", "supply_chain", "capacity", "technology", "strategy", "market_expansion",
    "demand", "volume", "pricing", "inventory",
    "shareholder_return", "financing", "balance_sheet", "dilution", "risk", "cybersecurity",
    "regulatory", "legal", "macro", "currency_fx", "geopolitical", "leadership"
]

# --- 2. Data Models ---

class CompanyInfo(BaseModel):
    name: str
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class Chunk(BaseModel):
    """Explicit model for retrieved chunks to ensure type safety across nodes."""
    event_id: str
    chunk_id: str
    source_type: Literal["news", "earnings_transcript"]
    date: str  # ISO Format
    content: str
    source: str
    url: Optional[str] = None
    raw_json_sha256: str
    cosine_sim: float

class QueryMetadata(BaseModel):
    """Stores the parameters used in the Retriever Node."""
    calendar_year: int
    calendar_month: int
    top_k: int = 3

class Citation(BaseModel):
    chunk_id: CoercedStr
    quote: str

class Catalyst(BaseModel):
    action: Literal["create", "update"]
    catalyst_id: Optional[str] = ""
    catalyst_type: CatalystType
    title: str
    summary: str
    sentiment: Literal[1, -1]
    magnitude: Literal[1, 0, -1]
    impact_area: ImpactArea
    time_horizon: Literal[0, 1, 2]
    citations: List[Citation]
    is_valid: bool = False
    rejection_reason: Optional[str] = None

    @field_validator("impact_area", mode="before")
    @classmethod
    def normalize_impact_area(cls, v):
        if isinstance(v, str):
            return _IMPACT_AREA_ALIASES.get(v.lower().strip(), v)
        return v

# --- 3. The Graph State ---
class CatalystSession(TypedDict):
    company_info: CompanyInfo
    query_params: QueryMetadata
    
    # Use the wrapped reducers here
    raw_chunks: Annotated[List[Chunk], set_reducer]
    existing_catalysts: Optional[List[Catalyst]] = []
    
    # Stage 1: Grouping Output
    uuid_groups: Annotated[List[List[str]], set_reducer]
    
    # Stage 2 & 3: Final Results
    final_catalysts: Annotated[List[Catalyst], set_reducer]
    
    errors: Annotated[List[str], add_reducer]


# --- Helper: State Factory ---

def catalyst_session_factory(
    tic: str,
    company_name: str,
    sector: str = None,
    industry: str = None,
    company_description: str = None,
    calendar_year: int = 2026,
    calendar_month: int = 3,
    top_k: int = 3
) -> Dict:
    """Initializes the state with required nested objects."""
    return {
        "company_info": CompanyInfo(
            ticker=tic, 
            name=company_name, 
            sector=sector,
            industry=industry,
            description=company_description
        ),
        "query_params": QueryMetadata(
            calendar_year=calendar_year, 
            calendar_month=calendar_month, 
            top_k=top_k
        ),
        "raw_chunks": [],
        "existing_catalysts": [], 
        "uuid_groups": [],
        "final_catalysts": [],
        "errors": []
    }