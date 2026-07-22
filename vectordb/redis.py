import redis
import re
from dataclasses import dataclass
from redis.commands.search.query import Query
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from config.llm_gateway import EMBEDDING_MODEL
from utils.gen_unique_ids import generate_unique_ids
import numpy as np
from langchain_core.documents import Document
from output_val.structured_outputs import SearchFilter


class RedisVectorStore:
    def __init__(
        self,host="localhost",port=6379,index_name="sec-edgar", embedding = None):

        self.index_name = index_name

        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=False,
        )

        self.schema = (
            TextField("content"),
            TagField("ticker"),
            TagField("form"),
            TagField("section"),
            TagField("source"),
            TagField("accession_number"),
            TagField("filing_date"),
            NumericField("filing_year"),
            NumericField("chunk_id"),

            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,
                    "DISTANCE_METRIC": "COSINE",
                    "M": 16,
                    "EF_CONSTRUCTION": 200,
                },
            ),
        )
        self.embedding = embedding or EMBEDDING_MODEL
        
        
    def create_index(self):
        try:
            self.client.ft(self.index_name).info()
        except redis.ResponseError:
            self.client.ft(self.index_name).create_index(
                self.schema,
                definition=IndexDefinition(
                    prefix=["doc:"], index_type=IndexType.HASH
                )
            )
    
    def add_documents(self, documents):

        for doc in documents:

            key = "doc:" + generate_unique_ids(doc)

            embedding = self.embedding.embed_documents([doc.page_content])[0]

            #convert to numpy float32 array first
            embedding = np.asarray(
                embedding,
                dtype=np.float32,
            )

            self.client.hset(
                key,
                mapping={
                    "content": doc.page_content,
                    "ticker": doc.metadata.get("ticker", ""),
                    "form": doc.metadata.get("form", ""),
                    "section": doc.metadata.get("section", ""),
                    "source": doc.metadata.get("source", ""),
                    "accession_number": doc.metadata.get("accession_number", ""),
                    "filing_date": doc.metadata.get("filing_date", ""),
                    "filing_year": doc.metadata.get("filing_year", 0),
                    "chunk_id": doc.metadata.get("chunk_id", 0),
                    "embedding": embedding.tobytes(),
                },)

    @staticmethod
    def _escape_tag(value):
        return re.sub(r"([,.<>\{\}\[\]\"':;!@#\$%\^&*()\-+=~\s])", r"\\\1", str(value))

    @staticmethod
    def _decode(value):
        return value.decode("utf-8") if isinstance(value, bytes) else value

    def _build_filter_query(self, filter: SearchFilter | None):
        if not filter:
            return "*"

        clauses = []

        if filter.ticker:
            clauses.append(f"@ticker:{{{self._escape_tag(filter.ticker)}}}")
        if filter.forms:
            forms = "|".join(self._escape_tag(form) for form in filter.forms)
            clauses.append(f"@form:{{{forms}}}")
        if filter.sections:
            sections = "|".join(
                self._escape_tag(section) for section in filter.sections
            )
            clauses.append(f"@section:{{{sections}}}")
        if filter.source:
            clauses.append(f"@source:{{{self._escape_tag(filter.source)}}}")
        if filter.start_year is not None:
            end_year = filter.end_year or filter.start_year
            clauses.append(f"@filing_year:[{filter.start_year} {end_year}]")

        return " ".join(clauses) or "*"
        

    def similarity_search(
        self,
        query,
        k=15,
        filter: SearchFilter | None = None,
    ):

        embedding = self.embedding.embed_query(query)

        embedding = np.asarray(
            embedding,
            dtype=np.float32,
        )

        filter_query = self._build_filter_query(filter)
        query_prefix = "*" if filter_query == "*" else f"({filter_query})"

        q = (
            Query(
                f"{query_prefix}=>[KNN {k} @embedding $vec AS score]"
            )
            .sort_by("score")
            .return_fields(
                "content",
                "ticker",
                "form",
                "section",
                "source",
                "accession_number",
                "filing_date",
                "filing_year",
                "chunk_id",
                "score",
            )
            .dialect(2)
        )

        results = self.client.ft(self.index_name).search(
            q, 
            query_params={
                "vec": embedding.tobytes(),
            },
        )

        docs = []

        for hit in results.docs:

            docs.append(
                Document(
                    page_content=self._decode(hit.content),
                    metadata={
                        "ticker": self._decode(hit.ticker),
                        "form": self._decode(hit.form),
                        "section": self._decode(hit.section),
                        "source": self._decode(hit.source),
                        "accession_number": self._decode(hit.accession_number),
                        "filing_date": self._decode(hit.filing_date),
                        "filing_year": int(hit.filing_year),
                        "chunk_id": int(hit.chunk_id),
                        "score": float(hit.score),
                    },
                )
            )

        return docs

    def clear(self):
        try:
            self.client.ft(self.index_name).dropindex(delete_documents=True)
        except redis.ResponseError:
            pass
        return "Vectorstore cleared successfully."

redis_store = RedisVectorStore()
