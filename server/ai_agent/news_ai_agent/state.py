from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# Define enums for the state model
Category = Literal["fundamental", "market_perception", "technical", "noise"]
TimeHorizon = Literal["short_term", "mid_term", "long_term"]
ImpactMag = Literal["minor", "moderate", "major"]
Sentiment = Literal["positive", "neutral", "negative"]
AffectedDimensions = Literal[
    "revenue", "profit", "cash", "cost", "risk", "technology", "sentiment"
]

class News(BaseModel):
    # Inputs
    ticker: str
    headline: str
    summary: str
    publisher: str
    publish_date: str  # ISO 8601 with time, e.g., "2025-10-03 12:15:05"

    # Stage 1 outputs
    category: Optional[Category] = None
    event_type: Optional[str] = None

    # Stage 2 outputs
    time_horizon: Optional[TimeHorizon] = None
    duration: Optional[str] = None
    impact_magnitude: Optional[ImpactMag] = None
    affected_dimensions: Optional[List[AffectedDimensions]] = None
    sentiment: Optional[Sentiment] = None