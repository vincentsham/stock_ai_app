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
    ticker: str = Field(..., description="Stock ticker symbol, e.g., AAPL")
    headline: str = Field(..., description="Headline of the news article")
    summary: str = Field(..., description="Summary or content of the news article")
    url: str = Field(..., description="URL of the news article")
    publisher: str = Field(..., description="Publisher of the news article")
    publish_date: str = Field(..., description="Publish date of the news article")

    # Stage 1 outputs
    category: Optional[Category] = Field(None, description="Category of the news")
    event_type: Optional[str] = Field(None, description="Event type of the news")

    # Stage 2 outputs
    time_horizon: Optional[TimeHorizon] = Field(None, description="Time horizon for the news impact")
    duration: Optional[str] = Field(None, description="Duration of the news impact")
    impact_magnitude: Optional[ImpactMag] = Field(None, description="Impact magnitude of the news")
    affected_dimensions: Optional[List[AffectedDimensions]] = Field(None, description="Affected dimensions of the news")
    sentiment: Optional[Sentiment] = Field(None, description="Sentiment of the news")