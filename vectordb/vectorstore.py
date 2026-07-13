    
from langchain_chroma import Chroma
from config.llm_gateway import EMBEDDING_MODEL
from itertools import batched
from tools.gen_unique_ids import generate_unique_ids

_current_vectorstore = None

def vectordb_store(chunks):
    global _current_vectorstore
    
    BATCH_SIZE = 64
    
    _current_vectorstore = Chroma(
        embedding_function=EMBEDDING_MODEL,
        persist_directory='./chroma_db'
    )
    
    for batch in batched(chunks, BATCH_SIZE): 
        batch_list = list(batch)
        
        #deterministic vector IDS
        batch_ids = [generate_unique_ids(doc) for doc in batch_list]
        
        _current_vectorstore.add_documents(documents=batch_list,
                                           ids = batch_ids)
    
    return _current_vectorstore

def get_vectorstore():
    return _current_vectorstore

def clear_vectorstore():
    global _current_vectorstore
    _current_vectorstore = None
    return "Vectorstore cleared successfully."
