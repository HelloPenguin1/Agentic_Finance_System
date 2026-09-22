from copy import deepcopy

from langchain_classic.schema import Document

MAX_WORDS_PER_CHUNK = 500
OVERLAP_WORDS = 50

# 10-Q item numbers repeat across Part I and Part II (e.g. both have an
# "Item 1" and "Item 2" that mean different things). 10-Ks don't have this
# problem — every 10-K item number is unique — so only 10-Qs need part-aware
# extraction (via chunks_for_part + chunks_for_item, see below).
TEN_Q_PARTS = {
    "Part I": ["Item 1", "Item 2", "Item 3", "Item 4"],
    "Part II": ["Item 1", "Item 1A", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"],
}


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


def _make_metadata(ticker, filing, part, item):
    return {
        "ticker": ticker,
        "form": filing.form,
        "filing_date": str(filing.filing_date),
        "filing_year": filing.filing_date.year,
        "accession_number": filing.accession_number,
        "part": part,                                  # None for 10-K, "Part I"/"Part II" for 10-Q
        "item": item,                                   # e.g. "Item 2"
        "section": f"{part}, {item}" if part else item,  # combined label, matches WORKER_CONFIG strings
        "source": "SEC",
    }


def _extract_text(chunk):
    if isinstance(chunk, str):
        return chunk
    return getattr(chunk, "text", str(chunk))


def _process_chunk(chunk, metadata, seen_chunks, global_chunk_idx, all_docs):
    """Original per-raw-chunk filtering, dedup, and splitting — unchanged."""
    text = _extract_text(chunk)
    text = " ".join(text.split())

    if len(text) < 40:
        return global_chunk_idx

    if len(text.split()) < 25:
        return global_chunk_idx

    if text in seen_chunks:
        return global_chunk_idx

    seen_chunks.add(text)

    split_docs, global_chunk_idx = split_large_chunk(
        text=text,
        metadata=metadata,
        chunk_id=global_chunk_idx,
    )
    all_docs.extend(split_docs)
    return global_chunk_idx


def filings_to_langchain_docs_2(filings, ticker):
    """
    Convert SEC filings into LangChain Documents.

    Features
    --------
    - Normalizes whitespace.
    - Removes duplicate chunks within the same filing.
    - Filters tiny chunks.
    - Splits oversized chunks into overlapping sub-chunks.
    - For 10-Qs, tags each raw chunk with its correct (Part, Item) so that
      e.g. "Part I, Item 1" (Financial Statements) and "Part II, Item 1"
      (Legal Proceedings) are never merged under a single "Item 1" label.
      This uses chunks_for_part(part) and chunks_for_item(item) together:
      both draw from the same underlying chunk list, so a chunk returned
      by both calls is identified by object identity (id()) as belonging
      to that exact (part, item) pair — no private API needed, and the
      original block-level chunk granularity (and per-raw-chunk dedup) is
      preserved exactly as in the 10-K path.
    """

    all_docs = []

    for filing in filings:
        try:
            obj = filing.obj()
            chunk_doc = obj.chunked_document

            seen_chunks = set()
            global_chunk_idx = 0

            if filing.form == "10-Q":
                for part, item_list in TEN_Q_PARTS.items():
                    # Materialize once per part; chunks_for_part is a generator.
                    part_chunks = list(chunk_doc.chunks_for_part(part))
                    part_chunk_ids = {id(c) for c in part_chunks}

                    for item in item_list:
                        for chunk in chunk_doc.chunks_for_item(item):
                            # chunks_for_item alone mixes Part I and Part II
                            # matches for the same item number — keep only
                            # the ones that also belong to this part.
                            if id(chunk) not in part_chunk_ids:
                                continue

                            metadata = _make_metadata(ticker, filing, part, item)
                            global_chunk_idx = _process_chunk(
                                chunk, metadata, seen_chunks, global_chunk_idx, all_docs
                            )

            else:
                # 10-K (and anything else): item numbers are unique, no
                # Part-level collisions, so the original approach is fine.
                items = chunk_doc.list_items()

                for item in items:
                    for chunk in chunk_doc.chunks_for_item(item):
                        metadata = _make_metadata(ticker, filing, None, item)
                        global_chunk_idx = _process_chunk(
                            chunk, metadata, seen_chunks, global_chunk_idx, all_docs
                        )

        except Exception as e:
            print(
                f"Warning: Failed to parse {filing.form} "
                f"({filing.accession_number}) for {ticker}. Error: {e}"
            )
            continue

    return all_docs