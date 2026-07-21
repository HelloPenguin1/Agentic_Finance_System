import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from graph.workflow import workflow
from vectordb.vectorstore import clear_vectorstore

app = FastAPI(
    title="Multi-Agent SEC Filing Intelligence Assistant",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    user_question: str

@app.get("/")
async def read_root():
    return {'message':'Welcome'}

@app.post("/query")
async def user_query(query: QueryRequest):
    result = workflow.invoke(
        {'messages': [HumanMessage(content=query.user_question)]}
        ,
        config={
            "configurable":{
                "thread_id": "demo-user"
            }
        }
        )
    return {'result': result.get("completed_sections")} 

@app.post("/clear_vectorstore")
async def clear_vectorstore_endpoint():
    return {"message": clear_vectorstore()}


    
    