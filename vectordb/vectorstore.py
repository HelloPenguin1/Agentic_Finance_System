    
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL

_current_vectorstore = None

def vectordb_store(chunks):
    global _current_vectorstore
    _current_vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=EMBEDDING_MODEL,
        persist_directory='./chroma_db'
    )
    return _current_vectorstore

def get_vectorstore():
    return _current_vectorstore

def clear_vectorstore():
    global _current_vectorstore
    _current_vectorstore = None
    return "Vectorstore cleared successfully."
