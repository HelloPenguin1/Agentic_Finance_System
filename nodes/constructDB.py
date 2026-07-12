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
        ##Modification Idea
        ## perhaps add if statements here to not fetch every 10-k , 10-q and 8-k document if intennt is any other than report
        filings = self.fetcher.fetch_filings(
        ticker=state["company"],
        start_year=state["start_year"],
        end_year=state["end_year"])
            
        filings = list(filings)
    
        chunks = filings_to_langchain_docs(filings=filings, ticker=state["company"])
        vectordb_store(chunks)
        
        return { }

    
        

