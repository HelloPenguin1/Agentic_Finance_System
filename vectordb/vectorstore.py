import shutil
from pathlib import Path
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL
from itertools import batched
from tools.gen_unique_ids import generate_unique_ids

_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"


_current_vectorstore = None


def vectordb_store(chunks):
    global _current_vectorstore

    BATCH_SIZE = 64

    _current_vectorstore = Chroma(
        embedding_function=EMBEDDING_MODEL,
        persist_directory=str(_PERSIST_DIR)
    )

    for batch in batched(chunks, BATCH_SIZE):
        batch_list = list(batch)

        # deterministic vector IDs
        batch_ids = [generate_unique_ids(doc) for doc in batch_list]

        _current_vectorstore.add_documents(documents=batch_list, ids=batch_ids)

    return _current_vectorstore


def get_vectorstore():
    return _current_vectorstore


def clear_vectorstore():
    global _current_vectorstore

    if _PERSIST_DIR.exists():
        shutil.rmtree(_PERSIST_DIR)

    _current_vectorstore = None
    return "Vectorstore cleared successfully."
