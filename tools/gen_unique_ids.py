import hashlib


def generate_unique_ids(doc):
    metadata = doc.metadata
    ticker = metadata.get("ticker")
    form = metadata.get("form")
    chunk_id = metadata.get("chunk_id")
    
    if ticker and form and chunk_id:
        return f"{ticker}_{form}_{chunk_id}"
    else:
        #fallback: hash the actual content
        content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
        source = metadata.get("source", "unknown")
        return f"{source}_{content_hash}"