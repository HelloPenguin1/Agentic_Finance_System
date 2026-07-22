"""FastAPI entry point for the Agentic SEC Filing Analysis Assistant."""

import sys
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, HTTPException, status
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from graph.workflow import workflow
from output_val.structured_outputs import Citation
from vectordb.redis import redis_store


app = FastAPI(
    title="Agentic SEC Filing Analysis Assistant",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    """A natural-language question about SEC filings."""

    query: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    """The synthesized graph answer and its supporting citations."""

    answer: str
    citations: List[Citation]


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a welcome message."""
    return {"message": "Agentic SEC Filing Analysis Assistant API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm that the API is running."""
    return {"status": "healthy"}


@app.post("/clear_vectorstore")
def clear_redis_store_endpoint() -> dict[str, str]:
    """Remove the stored vector database contents."""
    return {"message": redis_store.clear()}


@app.post("/query", response_model=AnalyzeResponse)
def query_filings(request: QueryRequest) -> AnalyzeResponse:
    """Run the compiled LangGraph workflow for a financial question."""
    try:
        result = workflow.invoke({"messages": [HumanMessage(content=request.query)]})
        final_response: Any = result.get("final_response")

        if not final_response:
            return AnalyzeResponse(
                answer="No relevant disclosures were found.", citations=[]
            )

        if isinstance(final_response, dict):
            answer = final_response.get("content", "")
            raw_citations = final_response.get("citations", [])
        else:
            answer = getattr(final_response, "content", "")
            raw_citations = getattr(final_response, "citations", [])

        if not answer:
            return AnalyzeResponse(
                answer="No relevant disclosures were found.", citations=[]
            )

        return AnalyzeResponse(answer=answer, citations=raw_citations or [])
    except Exception as e:
        print(e)
        raise
