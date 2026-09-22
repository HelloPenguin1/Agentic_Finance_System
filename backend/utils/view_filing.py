"""
Quick filing browser: ticker -> pick filing -> pick section -> read chunks.
Put this next to fetch_filings.py and run:  python view_filing.py
"""

from fetch_filings import FilingFetcher


def clean(chunk):
    text = chunk if isinstance(chunk, str) else getattr(chunk, "text", str(chunk))
    return " ".join(text.split())


ticker = input("Ticker (e.g. NVDA): ").strip().upper()
start_year = int(input("Start year (e.g. 2025): "))
form = input("Form (10-K or 10-Q): ").strip().upper()

# 1. list filings
filings = list(FilingFetcher().fetch_filings(ticker, start_year, [form], end_year=2026))
if not filings:
    raise SystemExit("No filings found.")

for i, f in enumerate(filings):
    print(f"[{i}] {f.form}  filed {f.filing_date}  {f.accession_number}")

filing = filings[int(input("\nPick filing #: "))]
print(f"\nLoading {ticker} {filing.form} {filing.filing_date} ...")
chunked = filing.obj().chunked_document
items = chunked.list_items()

# 2. pick a section, read it, repeat
while True:
    print("\nSections:")
    for i, item in enumerate(items):
        preview = ""
        for chunk in chunked.chunks_for_item(item):
            text = clean(chunk)
            if len(text.split()) >= 25:
                preview = text[:80]
                break
        print(f"[{i}] {item:10s} | {preview}...")

    choice = input("\nSection # (or q to quit): ").strip()
    if choice.lower() == "q":
        break

    item = items[int(choice)]
    seen = set()
    n = 0
    print(
        f"\n===== {ticker} | {filing.form} | {filing.accession_number} | {item} ====="
    )

    for chunk in chunked.chunks_for_item(item):
        text = clean(chunk)
        # same filters as your ingestion script, so you see what ChromaDB sees
        if len(text.split()) < 25 or text in seen:
            continue
        seen.add(text)
        print(f"\n--- chunk {n} ({len(text.split())} words) ---\n{text}")
        n += 1

    print(f"\n({n} chunks in {item})")
