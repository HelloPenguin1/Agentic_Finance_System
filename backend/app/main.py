"""FastAPI entry point for the Agentic SEC Filing Analysis Assistant."""

import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from output_val.structured_outputs import Citation  
from vectordb.vectorstore import clear_vectorstore
from nodes.constructDB import ConstructDB

from typing import Any
from langchain_core.messages import HumanMessage
from graph.workflow import workflow


construct_db = ConstructDB()


app = FastAPI(
    title="Agentic SEC Filing Analysis Assistant",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    """A natural-language question about SEC filings."""

    query: str = Field(min_length=1)


class IngestRequest(BaseModel):
    """A company and filing year to ingest from SEC Edgar."""

    company: str = Field(min_length=1)
    filing_year: Optional[int] = None
    filing_start_year: Optional[int] = None
    filing_end_year: Optional[int] = None


class AnalyzeResponse(BaseModel):
    """The synthesized graph answer and its supporting citations."""

    answer: str
    citations: List[Citation]


class IngestResponse(BaseModel):
    """The result of an ingestion request."""

    message: str
    chunks_indexed: int


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a welcome message."""
    return {"message": "Agentic SEC Filing Analysis Assistant API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm that the API is running."""
    return {"status": "healthy"}


@app.post("/clear_vectorstore")
def clear_vectorstore_endpoint() -> dict[str, str]:
    """Remove the stored vector database contents."""
    return {"message": clear_vectorstore()}


@app.post("/query", response_model=AnalyzeResponse)
def query_filings(request: QueryRequest) -> AnalyzeResponse:
    """Answer a question using previously ingested SEC filing chunks."""
    result = workflow.invoke({"messages":[HumanMessage(content=request.query)]})
    final_response: Any = result.get("final_response")
    if not final_response:
        return {"answer": "No relevant disclosures were found.", "citations": []}
    
    answer = final_response.get("content", "")
    citations = final_response.get("citations",[])
    
    if not answer:
        return {"answer": "No relevant disclosures were found.", "citations": []}

    return {"answer": answer, 
            "citations": citations or []}


@app.post("/ingest", response_model=IngestResponse)
def ingest_filings(request: IngestRequest) -> IngestResponse:
    """Retrieve, chunk, embed, and index one company's SEC filings."""
    filing_year = request.filing_year or request.filing_start_year

    if filing_year is None:
        raise HTTPException(status_code=400, detail="Provide filing_year or filing_start_year.")

    chunk_count = construct_db.build_vectordb(
        company=request.company,
        filing_year=filing_year,
    )

    return {
        "message": "Ingestion completed successfully.",
        "chunks_indexed": chunk_count,
    }
