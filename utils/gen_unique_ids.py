import hashlib


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