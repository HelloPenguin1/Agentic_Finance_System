from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from .state import GraphState
from nodes.query_decompose import QueryDecompose
from nodes.constructDB import Construct_DB
from nodes.workers import revenue_agent, profitability_agent, liquidity_agent, management_agent, risk_agent
from nodes.assign_workers import assign_workers
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
load_dotenv()
import os

DATABASE_URI = os.getenv("DB_URI")

conn = psycopg.connect(
    DATABASE_URI,
    autocommit=True,
    row_factory=dict_row
)

workflow = StateGraph(GraphState)
construct_db = Construct_DB()

#Node Defintions
workflow.add_node("constructdb", construct_db.build_vectordb)
workflow.add_node("query_decompose", QueryDecompose)

workflow.add_node("revenue_agent", revenue_agent)
workflow.add_node("profitability_agent", profitability_agent)
workflow.add_node("risk_agent", risk_agent)
workflow.add_node("management_agent", management_agent)
workflow.add_node("liquidity_agent", liquidity_agent)


#Edge Defintion
workflow.add_edge(START, "query_decompose")
workflow.add_edge("query_decompose", "constructdb")
workflow.add_conditional_edges("constructdb", 
                               assign_workers, #routing function
                               ["revenue_agent",
                                "liquidity_agent",
                                "profitability_agent", 
                                "management_agent", 
                                "risk_agent"]) 
                               
workflow.add_edge("revenue_agent", END)
workflow.add_edge("liquidity_agent", END)
workflow.add_edge("profitability_agent", END)
workflow.add_edge("management_agent", END)
workflow.add_edge("risk_agent", END)

checkpointer = PostgresSaver(conn)
checkpointer.setup()

workflow = workflow.compile(
    checkpointer=checkpointer,
)


if __name__=='__main__':
    response = workflow.invoke({'messages': [HumanMessage(content='Apple revenue 2024')]})
    print(response)