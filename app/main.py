import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from pydantic import BaseModel
from graph.workflow import workflow


app = FastAPI(
    title="Multi-Agent Finance Assistant",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    user_question: str
    

@app.get("/")
async def read_root():
    return {'message':'Welcome'}

@app.post("/query")
async def user_query(query: QueryRequest):
    result = workflow.invoke({'query':query.user_question})
    return {'result': result.get("completed_sections")}
