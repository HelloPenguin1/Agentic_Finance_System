from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class queryDecompose(BaseModel):
    """Structured output for query llm"""
    company: str
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    intent: Literal["report", "specific"] = "specific"
    requested_sections: List[Literal["revenue", "profitability", "liquidity", "risk", "management"]] = Field(default_factory=list)
    optimized_query: str


class sectionOutput(BaseModel):
    """LLM generation for section-wise answer"""
    heading: str
    content: str