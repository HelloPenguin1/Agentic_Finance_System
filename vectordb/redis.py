from sentence_transformers import SentenceTransformer
import redis
from redis.commands.search.query import Query
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.json.path import Path
from config.llm_gateway import EMBEDDING_MODEL
from utils.gen_unique_ids import generate_unique_ids
import numpy as np
from langchain_core.documents import Document

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
            TagField("company"),
            TagField("section"),

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
        except:
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
                    "company": doc.metadata.get("company", ""),
                    "section": doc.metadata.get("section", ""),
                    "accession_number": doc.metadata.get("accession_number", ""),
                    "embedding": embedding.tobytes(),
                },)
        

    def similarity_search(
        self,
        query,
        k=15,
    ):

        embedding = EMBEDDING_MODEL.embed_query(query)

        embedding = np.asarray(
            embedding,
            dtype=np.float32,
        )

        q = (
            Query(
                f"*=>[KNN {k} @embedding $vec AS score]"
            )
            .sort_by("score")
            .return_fields(
                "content",
                "company",
                "section",
                "accession_number"
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
                    page_content=hit.content,
                    metadata={
                        "company": hit.company,
                        "section": hit.section,
                        "accession_number": hit.section,
                        "score": float(hit.score),
                    },
                )
            )

        return docs

redis_store = RedisVectorStore()