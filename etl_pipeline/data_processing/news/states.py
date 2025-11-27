from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import IntEnum

# Define enums for the state model
Category = Literal["fundamental", "market_perception", "technical", "noise"]
AffectedDimensions = Literal[
    "revenue", "profit", "cash", "cost", "risk", "technology", "sentiment"
]
# ---- Enums / Literals ----
class Tri(IntEnum):
    NEG = -1
    NEU = 0
    POS = 1

class Horizon(IntEnum):
    SHORT = 0
    MID = 1
    LONG = 2


class News(BaseModel):
    # Inputs
    tic: str = Field(..., description="Stock ticker symbol, e.g., AAPL")
    company_name: str = Field(..., description="Full company name, e.g., Apple Inc.")
    industry: str = Field(..., description="Industry of the company, e.g., Technology")
    sector: str = Field(..., description="Sector of the company, e.g., Consumer Electronics")
    company_description: str = Field(..., description="Description of the company")

    # News article details
    headline: str = Field(..., description="Headline of the news article")
    summary: str = Field(..., description="Summary or content of the news article")
    url: str = Field(..., description="URL of the news article")
    publisher: str = Field(..., description="Publisher of the news article")
    published_at: str = Field(..., description="Publish date of the news article")

    # Stage 1 outputs
    category: Optional[Category] = Field(None, description="Category of the news")
    event_type: Optional[str] = Field(None, description="Event type of the news")

    # Stage 2 outputs
    time_horizon: Optional[Horizon] = Field(None, description="Time horizon for the news impact")
    duration: Optional[str] = Field(None, description="Duration of the news impact")
    impact_magnitude: Optional[Tri] = Field(None, description="Impact magnitude of the news")
    affected_dimensions: Optional[List[AffectedDimensions]] = Field(None, description="Affected dimensions of the news")
    sentiment: Optional[Tri] = Field(None, description="Sentiment of the news")