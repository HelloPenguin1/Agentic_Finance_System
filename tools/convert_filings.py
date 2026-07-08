from langchain_classic.schema import Document

        
from langchain_classic.schema import Document

def filings_to_langchain_docs(filings, ticker):
    """Convert filings into LangChain Document objects"""

    all_docs = []  # global accumulator

    for filing in filings:
        try:
            obj = filing.obj()
            chunk_doc = obj.chunked_document
            items = chunk_doc.list_items()

            for item in items:
                item_chunks = chunk_doc.chunks_for_item(item)  # local variable

                for i, c in enumerate(item_chunks):
                    if isinstance(c, str):
                        text = c
                    else:
                        text = getattr(c, "text", str(c))

                    # filtering
                    if not text or len(text.strip()) < 40:
                        continue
                    if "TableBlock" in text:
                        continue

                    all_docs.append(
                        Document(
                            page_content=text,
                            metadata={
                                "ticker": ticker,
                                "form": filing.form,
                                "filing_date": str(filing.filing_date),
                                "section": item,
                                "chunk_id": i,
                                "source": "SEC"
                            }
                        )
                    )

        except Exception:
            continue

    return all_docs
