import json
from pathlib import Path

LOOKUP_PATH = Path(__file__).resolve().parent.parent / "data" / "company_lookup.json"

with LOOKUP_PATH.open("r", encoding="utf-8") as fh:
    COMPANY_LOOKUP = json.load(fh)


def resolve_company(name: str):
    """This function takes in LLM-extracted name from query and hash-looks up the company ticker"""
    name = name.lower().strip()
    return COMPANY_LOOKUP.get(name)