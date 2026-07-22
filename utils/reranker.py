from langchain_core.documents import Document
from config.llm_gateway import RERANKER_MDOEL

def rerank_documents(query: str, docs: list[Document], top_k: int = 5):
    """
    Rerank retrieved LangChain Documents.

    Returns the top_k documents ordered by relevance.
    """

    if not docs:
        return []

    pairs = [(query, doc.page_content) for doc in docs]
    scores = RERANKER_MDOEL.predict(pairs)

    ranked = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True,
    )

    return [doc for _, doc in ranked[:top_k]]


def build_context(docs: list[Document]) -> str:
    """
    Convert reranked Documents into JSON
    that is passed to the LLM.
    """

    context = []

    for doc in docs:
        context.append(
            {
                "chunk_id": doc.metadata.get("chunk_id"),
                "form": doc.metadata.get("form"),
                "section": doc.metadata.get("section"),
                "accession_number": doc.metadata.get("accession_number"),
                "text": doc.page_content,
            }
        )

    return context



if __name__ == "__main__":
    sample_query = "What were Apple's revenue trends in 2024?"
    sample_docs = [
        Document(
            page_content="Apple reported revenue growth in fiscal 2024 driven by services and iPhone demand.",
            metadata={"source": "10-K", "section": "Item 7", "filing_year": 2024},
        ),
        Document(
            page_content="The company faced supply chain risks and competition in consumer electronics.",
            metadata={"source": "10-K", "section": "Item 1A", "filing_year": 2024},
        ),
        Document(
            page_content="Revenue increased year over year as hardware and services expanded globally.",
            metadata={"source": "10-Q", "section": "Item 7", "filing_year": 2024},
        ),
    ]

    ranked_docs = rerank_documents(sample_query, sample_docs, top_k=2)

    print("Query:", sample_query)
    print("Top ranked documents:")
    for idx, doc in enumerate(ranked_docs, start=1):
        print(f"{idx}. {doc.page_content}")
        print(f"   Metadata: {doc.metadata}")       