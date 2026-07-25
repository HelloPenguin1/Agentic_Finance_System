import shutil
from pathlib import Path
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL
from itertools import batched
from utils.gen_unique_ids import generate_unique_ids
import logging
import gc
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if os.getenv("K_SERVICE"):  # Running on Cloud Run
    _PERSIST_DIR = Path("/tmp/chroma_db")
else:  # Running locally
    _PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
    
    
_PERSIST_DIR.mkdir(parents=True, exist_ok=True)


BATCH_SIZE = 350  

def get_vectorstore():
    return Chroma(
        embedding_function=EMBEDDING_MODEL,
        persist_directory=str(_PERSIST_DIR),
    )

def vectordb_store(vectordb, chunks):
    logger.info(f"Preparing to insert {total_chunks} chunks")
    
    # Convert chunks to a list once to enable slicing and accurate sizing
    chunks_list = list(chunks)
    total_chunks = len(chunks_list)
    
    for i, batch in enumerate(batched(chunks_list, BATCH_SIZE)):
        batch_list = list(batch)

        # Generate deterministic IDs for the batch
        batch_ids = [generate_unique_ids(doc) for doc in batch_list]
        
        vectordb.add_documents(
            documents=batch_list,
            ids=batch_ids
        )
        logger.info(f"Batch {i+1} inserted successfully")
        
        
        processed_count = min((i + 1) * BATCH_SIZE, total_chunks)
        logger.info(f"Indexed batch {i + 1} ({processed_count}/{total_chunks} chunks)")
    
    #DEBUG STATEMENT
    count = vectordb._collection.count()
    logger.info(f"Collection now contains {count} documents")
    #END DEBUG STATEMENT

def clear_vectorstore():
    gc.collect()

    if _PERSIST_DIR.exists():
        shutil.rmtree(_PERSIST_DIR)
    logger.info('Vectorstore successfully cleared.')

    return "Vectorstore cleared successfully."