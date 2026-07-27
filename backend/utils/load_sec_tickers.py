import json
from pathlib import Path

import requests

headers = {"User-Agent": "dev@gmail.com"}
URL = "https://www.sec.gov/files/company_tickers.json"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "company_tickers.json"


def save_company_tickers(output_path: Path = OUTPUT_PATH) -> Path:
    """Getting company ticker information JSON from SEC API"""
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=2)

    return output_path


if __name__ == "__main__":
    saved_path = save_company_tickers()
    print(f"Saved company tickers to {saved_path}")
