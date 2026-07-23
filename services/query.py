"""Functions for answering questions from the existing vector database."""

from typing import Any

from langchain_core.messages import HumanMessage

from graph.workflow import workflow


def answer_query(query: str) -> dict[str, Any]:
    """Run the existing retrieval, reranking, and LangGraph answer workflow."""
    result = workflow.invoke({"messages": [HumanMessage(content=query)]})
    final_response: Any = result.get("final_response")

    if not final_response:
        return {"answer": "No relevant disclosures were found.", "citations": []}

    if isinstance(final_response, dict):
        answer = final_response.get("content", "")
        citations = final_response.get("citations", [])
    else:
        answer = getattr(final_response, "content", "")
        citations = getattr(final_response, "citations", [])

    if not answer:
        return {"answer": "No relevant disclosures were found.", "citations": []}

    return {"answer": answer, "citations": citations or []}
