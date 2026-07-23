from utils.convert_filings_updated import filings_to_langchain_docs
from utils.fetch_filings import FilingFetcher
from utils.resolve_c import resolve_company
from vectordb.vectorstore import get_vectorstore, vectordb_store
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ConstructDB:
    """Handles SEC filing ingestion into the vector database."""

    def build_vectordb(self, company: str, filing_year: int) -> int:
        """
        Fetch, chunk, embed, and index one company's SEC filings.

        Returns:
            Number of chunks indexed.
        """
        ticker = resolve_company(company) or company.upper()
        logger.info('Found company')

        filings = self.fetch_filing(ticker, filing_year)
        logger.info('Fetched filings')
        
        chunks = self.chunk_document(filings, ticker)
        logger.info('Chunked Documents')
        
        vectordb = get_vectorstore()
        self.index_chunks(vectordb, chunks)
        logger.info('Indexing chunks')

        return len(chunks)

    def fetch_filing(self, company: str, filing_year: int):
        """Retrieve the requested company's filings for one year."""
        fetcher = FilingFetcher()
        return list(
            fetcher.fetch_filings(
                ticker=company,
                start_year=filing_year,
            )
        )

    def chunk_document(self, filings, company: str):
        """Convert SEC filings into LangChain document chunks."""
        return filings_to_langchain_docs(
            filings=filings,
            ticker=company,
        )

    def index_chunks(self, vectordb, chunks) -> None:
        """Embed and store chunks in the vector database using the shared instance."""
        vectordb_store(
            vectordb,
            chunks,
        )