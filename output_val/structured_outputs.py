from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class queryDecompose(BaseModel):
    """Structured output for query llm"""
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    intent: Literal['report', 'qa'] = None
    
    