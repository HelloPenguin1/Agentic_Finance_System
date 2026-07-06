from edgar import *

class Fetcher:
    def __init__(self):
        set_identity('dev@gmail.com')
        self.filings = ""
        self.company = ""
        
    def fetch_filings(self, ticker: str,
                      start_date:str, 
                      end_date:str=None,
                      form_type:list[str] = ['10-K', '10-Q']):
        """This function fetches the filings and returns filing object"""

        self.company = Company(ticker)
        