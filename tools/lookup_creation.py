import json
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "company_tickers.json"
COMPANY_PATH = Path(__file__).resolve().parent.parent / "data" / "company_lookup.json"
TICKER_PATH = Path(__file__).resolve().parent.parent / "data" / "ticker_lookup.json"

 

if __name__=="__main__":
    with open(OUTPUT_PATH, "r") as f:
        data = json.load(f)

    company_lookup = {}
    ticker_lookup = {}

    for company in data.values():
        title = company["title"]
        ticker = company["ticker"]

        company_lookup[title.lower()] = ticker

        # Remove common suffixes
        short = (
            title.lower()
            .replace(" inc.", "")
            .replace(" inc", "")
            .replace(" corporation", "")
            .replace(" corp.", "")
            .replace(" corp", "")
            .replace(" plc", "")
            .replace(" ltd", "")
            .replace(" limited", "")
            .replace(",", "")
        ).strip()

        company_lookup[short] = ticker
        
    with COMPANY_PATH.open("w", encoding="utf-8") as f:
        json.dump(company_lookup, f, indent = 2)
    
   
    
        
    
    

    
    
    
    

