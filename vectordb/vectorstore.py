import shutil
from pathlib import Path
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL
from itertools import batched
from tools.gen_unique_ids import generate_unique_ids
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

        # deterministic vector IDs
        batch_ids = [generate_unique_ids(doc) for doc in batch_list]

        vectordb.add_documents(
            documents=batch_list, 
            ids=batch_ids)
        


def clear_vectorstore():
    gc.collect()

    if _PERSIST_DIR.exists():
        shutil.rmtree(_PERSIST_DIR)

    return "Vectorstore cleared successfully."
