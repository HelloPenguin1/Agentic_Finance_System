from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class queryDecompose(BaseModel):
    """Structured output for query llm"""
    company: str
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    intent: Literal['report', 'qa'] = None
    requested_sections: List[Literal["revenue", "profitability", "liquidity", "risk", "management"]] 
    
    