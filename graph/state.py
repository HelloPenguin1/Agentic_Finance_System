from typing_extensions import TypedDict
from typing import Optional, Literal, List, Any, Annotated
from langgraph.types import Send
from langchain_core.vectorstores import VectorStore
import operator
from langchain_core.documents import Document
from langgraph.graph.message import add_messages

from langchain_core.messages import AnyMessage

# SCHEMAS

class Citation(TypedDict):
    form: str
    section: str
    accession_number: str

class Finding(TypedDict):
    claim: str
    #support: Optional[str] = None   #changed from explanation
    citations: List[Citation]

class SectionOutput(TypedDict): 
    findings: List[Finding]

class final_answer(TypedDict):
    """LLM aggregates completed section findings and returns final answer"""
    content: str
    citations: List[Citation]

# GRAPH STATE 
    
class GraphState(TypedDict):
    """The persistent state memory of the workflow"""
    messages: Annotated[List[AnyMessage], add_messages]
    start_year: Optional[str]
    end_year: Optional[str] = None
    company: str
    intent: Literal["report", "specific"] = None

    optimized_query: str  # query rewriter
    requested_sections: List[str]  # update the query decomposer node to return the list of all agents if intent is report

    completed_sections: Annotated[
        List[SectionOutput],
        operator.add
    ]
    
    final_response: final_answer