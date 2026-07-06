from typing_extensions import TypedDict
from typing import Optional, Literal, List, Any, Annotated
from langgraph.types import Send
from langchain_core.vectorstores import VectorStore
import operator
from langchain_core.documents import Document


class GraphState(TypedDict):
    """The persistent state memory of the workflow"""
    query: str  #User sends a query
    
    #query decomposer output 
    start_date: Optional[str]
    end_date: Optional[str] = None
    company: List[str]
    intent: Literal['report', 'qa'] = None
    
    
    