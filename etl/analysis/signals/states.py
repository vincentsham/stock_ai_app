from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import IntEnum


class Binary(IntEnum):
    NO = 0
    YES = 1


from pydantic import BaseModel, Field, ConfigDict
from enum import IntEnum

class Binary(IntEnum):
    NO = 0
    YES = 1

class Signal(BaseModel):
    """
    Represents a lightweight triage decision to determine if a text chunk
    contains a relevant fundamental business signal.
    """
    model_config = ConfigDict(use_enum_values=True)

    is_signal: Binary = Field(
        ..., 
        description="Set to 1 (YES) if the chunk is relevant to the target company AND contains a fundamental business event; else 0 (NO)."
    )
    
    reason: str = Field(
        ..., 
        description="A concise rationale (max 8 words) for the triage decision (e.g., 'Fundamental: Guidance update' or 'Noise: Legal boilerplate')."
    )

    company_info: Optional[dict] = Field(
        None, 
        description="Optional field to hold metadata about the target company for context."
    )

    content: Optional[str] = Field(
        None, 
        description="Optional field to hold the text chunk being evaluated."
    )