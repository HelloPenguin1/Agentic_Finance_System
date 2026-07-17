from typing_extensions import TypedDict
from typing import Optional, Literal, List, Any, Annotated
from langgraph.types import Send
from langchain_core.vectorstores import VectorStore
import operator
from langchain_core.documents import Document
from langgraph.graph.message import add_messages

from langchain_core.messages import AnyMessage


class SectionOutput(TypedDict):
    section:str
    content:str

    
class GraphState(TypedDict):
    """The persistent state memory of the workflow"""
    messages: Annotated[List[AnyMessage], add_messages]

    # query decomposer output
    start_year: Optional[str]
    end_year: Optional[str] = None
    company: List[str]
    intent: Literal["report", "specific"] = None

    requested_sections: List[str]  # update the query decomposer node to return the list of all agents if intent is report

    completed_sections: Annotated[
        List[SectionOutput],
        operator.add
    ]
    
    final_report: str   

    retrieved_docs = []