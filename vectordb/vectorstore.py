import shutil
from pathlib import Path
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL
from itertools import batched
from utils.gen_unique_ids import generate_unique_ids
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)
import gc

_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
BATCH_SIZE= 16

def get_vectorstore():
    return Chroma(
        embedding_function=EMBEDDING_MODEL,
        persist_directory=str(_PERSIST_DIR)
    )
    



def vectordb_store(vectordb, chunks):
    for batch in batched(chunks, BATCH_SIZE):
        batch_list = list(batch)

        # Generate deterministic IDs once
        batch_ids = [generate_unique_ids(doc) for doc in batch_list]

        # Group documents by ID
        # duplicate_groups = defaultdict(list)
        # for doc_id, doc in zip(batch_ids, batch_list):
        #     duplicate_groups[doc_id].append(doc)

        # # Log duplicate documents
        # duplicates_found = False

        # for doc_id, docs in duplicate_groups.items():
        #     if len(docs) > 1:
        #         duplicates_found = True

        #         logger.error("=" * 100)
        #         logger.error("Duplicate document ID: %s", doc_id)
        #         logger.error("Number of copies: %d", len(docs))

        #         for idx, doc in enumerate(docs):
        #             logger.error("----- COPY %d -----", idx)
        #             logger.error("Metadata: %s", doc.metadata)
        #             logger.error(
        #                 "Content Preview:\n%s",
        #                 doc.page_content[:500].replace("\n", " ")
        #             )

        # if duplicates_found:
        #     raise ValueError(
        #         "Duplicate documents generated before Chroma. "
        #         "See log output above."
        #     )   

        vectordb.add_documents(
            documents=batch_list,
            ids=batch_ids
        )


def clear_vectorstore():
    gc.collect()

    if _PERSIST_DIR.exists():
        shutil.rmtree(_PERSIST_DIR)

    return "Vectorstore cleared successfully."
