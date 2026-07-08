from tools.fetch_filings import FilingFetcher
from tools.convert_filings import filings_to_langchain_docs
from vectordb.vectorstore import vectordb_store

class Construct_DB:
    def __init__(self):
        #Intialize the fetcher
        self.fetcher = FilingFetcher()
    
    def build_vectordb(self, state):
        """This node fetches SEC filing types, converts to Langchain docs, ingests into vectordb
        """
        if state["intent"]=='report':
            filings = self.fetcher.fetch_filings(
            ticker=state["company"],
            start_date=state["start_date"],
            end_date=state["end_date"])
            
        filings = list(filings)
    
        chunks = filings_to_langchain_docs(filings=filings, ticker=state["company"])
        vectordb_store(chunks)
        
        return {}

    
        

