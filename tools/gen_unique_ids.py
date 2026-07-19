import hashlib


# def generate_unique_ids(doc):
#     metadata = doc.metadata
    
#     accession = metadata.get("accession_number")
#     section = metadata.get("section","")
#     ticker = metadata.get("ticker")
#     form = metadata.get("form")
#     chunk_id = metadata.get("chunk_id")
#     filing_date = metadata.get("filing_date")
    
#     if ticker and form and chunk_id:
#         return f"{ticker}_{form}_{filing_date}_{chunk_id}"
#     else:
#         #fallback: hash the actual content
#         content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
#         source = metadata.get("source", "unknown")
#         return f"{source}_{content_hash}"


#new strat for unique ids
def generate_unique_ids(doc):
    metadata = doc.metadata

    accession = metadata.get("accession_number")
    section = metadata.get("section", "")
    text = doc.page_content.strip()

    if accession:
        raw = f"{accession}|{section}|{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # fallback
    ticker = metadata.get("ticker", "")
    form = metadata.get("form", "")
    filing_date = metadata.get("filing_date", "")

    raw = f"{ticker}|{form}|{filing_date}|{section}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()