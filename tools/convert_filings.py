from langchain_classic.schema import Document

from langchain_classic.schema import Document


def filings_to_langchain_docs(filings, ticker):
    """
    Convert SEC filings into LangChain Documents.

    - Normalizes whitespace.
    - Removes duplicate chunks within the same filing.
    - Filters very small chunks.
    """

    all_docs = []

    for filing in filings:
        try:
            obj = filing.obj()
            chunk_doc = obj.chunked_document
            items = chunk_doc.list_items()

            # Unique chunks seen within this filing
            seen_chunks = set()

            # Sequential chunk IDs for retained chunks
            global_chunk_idx = 0

            for item in items:
                item_chunks = chunk_doc.chunks_for_item(item)

                for chunk in item_chunks:

                    if isinstance(chunk, str):
                        text = chunk
                    else:
                        text = getattr(chunk, "text", str(chunk))

                    # Normalize whitespace
                    text = " ".join(text.split())

                    # Skip empty / tiny chunks
                    if len(text) < 40:
                        continue

                    # Skip duplicate chunks already seen in this filing
                    if text in seen_chunks:
                        continue

                    seen_chunks.add(text)

                    all_docs.append(
                        Document(
                            page_content=text,
                            metadata={
                                "ticker": ticker,
                                "form": filing.form,
                                "filing_date": str(filing.filing_date),
                                "filing_year": filing.filing_date.year,
                                "accession_number": filing.accession_number,
                                "section": item,
                                "chunk_id": global_chunk_idx,
                                "source": "SEC",
                            },
                        )
                    )

                    global_chunk_idx += 1

        except Exception as e:
            print(
                f"Warning: Failed to parse {filing.form} "
                f"({filing.accession_number}) for {ticker}. Error: {e}"
            )
            continue

    return all_docs


# def filings_to_langchain_docs(filings, ticker):
#     """Convert filings into LangChain Document objects"""

#     all_docs = []

#     for filing in filings:
#         try:
#             obj = filing.obj()
#             chunk_doc = obj.chunked_document
#             items = chunk_doc.list_items()
            
#             # 1. Initialize a global counter for the entire filing
#             global_chunk_idx = 0 

#             for item in items:
#                 item_chunks = chunk_doc.chunks_for_item(item)

#                 for chunk in item_chunks:
#                     if isinstance(chunk, str):
#                         text = chunk
#                     else:
#                         text = getattr(chunk, "text", str(chunk))

#                     # filtering
#                     if not text or len(text.strip()) < 40:
#                         continue

#                     all_docs.append(
#                         Document(
#                             page_content=text,
#                             metadata={
#                                 "ticker": ticker,
#                                 "form": filing.form,
#                                 "filing_date": str(filing.filing_date),
#                                 "filing_year": filing.filing_date.year, 
#                                 "accession_number":filing.accession_number, #added ths to metadata
#                                 "section": item,
#                                 "chunk_id": global_chunk_idx,  
#                                 "source": "SEC"
#                             }
#                         )
#                     )
                    
#                     global_chunk_idx += 1

#         except Exception as e:
#             # Replaced silent failure with a log so you know if a filing breaks
#             print(f"Warning: Failed to parse filing {filing.form} for {ticker}. Error: {e}")
#             continue

#     return all_docs


