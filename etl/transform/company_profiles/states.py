from typing import Optional
from pydantic import BaseModel, Field

class CompanyProfileState(BaseModel):
	# Input fields
	tic: str
	company_name: Optional[str] = None
	sector: Optional[str] = None
	industry: Optional[str] = None
	country: Optional[str] = None
	market_cap: Optional[int] = None
	employees: Optional[int] = None
	exchange: Optional[str] = None
	currency: Optional[str] = None
	website: Optional[str] = None
	description: str

	# Output fields (to be filled by the LLM)
	summary: Optional[str] = Field(None, description="200–300 token detailed summary")
	short_summary: Optional[str] = Field(None, description="100–150 word concise summary")
