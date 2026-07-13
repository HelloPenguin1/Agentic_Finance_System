from edgar import *
from edgar import Company, set_identity

class FilingFetcher:
    def __init__(self):
        set_identity("dev@gmail.com")


    def fetch_filings(
        self,
        ticker: str,
        start_year: int,
        form_types: list[str] = ['10-K', '10-Q', '8-K'],
        end_year: int | None = None,
    ):
        """
        Fetch financial SEC Edgar filings within a date range.
        """

        company = Company(ticker)

        start = f"{start_year}-01-01"
        end = f"{end_year}-12-31" if end_year else f"{start_year}-12-31"

        date_range = f"{start}:{end}"

        filings = company.get_filings(
            form=form_types,
            date=date_range
        )

        return filings
    

if __name__=="__main__":
    fetcher = FilingFetcher()
    filings = fetcher.fetch_filings(ticker= 'AAPL',
                                    start_year=2024,
                                    end_year=2025,
    )
    print(filings)
    
    