from copy import deepcopy

from langchain_classic.schema import Document

MAX_WORDS_PER_CHUNK = 500
OVERLAP_WORDS = 50


def split_large_chunk(
    text: str,
    metadata: dict,
    chunk_id: int,
    max_words: int = MAX_WORDS_PER_CHUNK,
    overlap: int = OVERLAP_WORDS,
):
    """
    Split oversized SEC chunks into smaller LangChain Documents.

    - Keeps all metadata identical.
    - Assigns a unique chunk_id to every resulting chunk.
    - Uses a small overlap to preserve context across boundaries.
    """

    words = text.split()

    if len(words) <= max_words:
        md = deepcopy(metadata)
        md["chunk_id"] = chunk_id

        return [
            Document(
                page_content=text,
                metadata=md,
            )
        ], chunk_id + 1

    docs = []
    step = max_words - overlap

    for start in range(0, len(words), step):
        sub_words = words[start:start + max_words]

        if not sub_words:
            break

        sub_text = " ".join(sub_words)

        md = deepcopy(metadata)
        md["chunk_id"] = chunk_id

        docs.append(
            Document(
                page_content=sub_text,
                metadata=md,
            )
        )

        chunk_id += 1

        if start + max_words >= len(words):
            break

    return docs, chunk_id


def filings_to_langchain_docs(filings, ticker):
    """
    Convert SEC filings into LangChain Documents.

    Features
    --------
    - Normalizes whitespace.
    - Removes duplicate chunks within the same filing.
    - Filters tiny chunks.
    - Splits oversized chunks into overlapping sub-chunks.
    """

    all_docs = []

    for filing in filings:
        try:
            obj = filing.obj()
            chunk_doc = obj.chunked_document
            items = chunk_doc.list_items()

            seen_chunks = set()
            global_chunk_idx = 0

            for item in items:
                item_chunks = chunk_doc.chunks_for_item(item)

                for chunk in item_chunks:

                    if isinstance(chunk, str):
                        text = chunk
                    else:
                        text = getattr(chunk, "text", str(chunk))

                    text = " ".join(text.split())

                    if len(text) < 40:
                        continue

                    if len(text.split()) < 25:
                        continue

                    if text in seen_chunks:
                        continue

                    seen_chunks.add(text)

                    metadata = {
                        "ticker": ticker,
                        "form": filing.form,
                        "filing_date": str(filing.filing_date),
                        "filing_year": filing.filing_date.year,
                        "accession_number": filing.accession_number,
                        "section": item,
                        "source": "SEC",
                    }

                    split_docs, global_chunk_idx = split_large_chunk(
                        text=text,
                        metadata=metadata,
                        chunk_id=global_chunk_idx,
                    )

                    all_docs.extend(split_docs)

        except Exception as e:
            print(
                f"Warning: Failed to parse {filing.form} "
                f"({filing.accession_number}) for {ticker}. Error: {e}"
            )
            continue

    return all_docs
