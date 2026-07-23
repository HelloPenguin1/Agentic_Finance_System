from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from .state import GraphState
from nodes.query_decompose import QueryDecompose
from nodes.workers import revenue_agent, profitability_agent, liquidity_agent, management_agent, risk_agent
from nodes.synthesizer import synthesizer_agent
from nodes.assign_workers import assign_workers
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
load_dotenv()
import os

# DATABASE_URI = os.getenv("DB_URI")

# conn = psycopg.connect(
#     DATABASE_URI,
#     autocommit=True,
#     row_factory=dict_row
# )

workflow = StateGraph(GraphState)
#Node Defintions
workflow.add_node("query_decompose", QueryDecompose)

workflow.add_node("revenue_agent", revenue_agent)
workflow.add_node("profitability_agent", profitability_agent)
workflow.add_node("risk_agent", risk_agent)
workflow.add_node("management_agent", management_agent)
workflow.add_node("liquidity_agent", liquidity_agent)
workflow.add_node("synthesizer_agent", synthesizer_agent)



#Edge Defintion
workflow.add_edge(START, "query_decompose")
workflow.add_conditional_edges("query_decompose",
                               assign_workers, #routing function
                               ["revenue_agent",
                                "liquidity_agent",
                                "profitability_agent", 
                                "management_agent",
                                "risk_agent"])
                               
workflow.add_edge("revenue_agent", "synthesizer_agent")
workflow.add_edge("liquidity_agent", "synthesizer_agent")
workflow.add_edge("profitability_agent", "synthesizer_agent")
workflow.add_edge("management_agent", "synthesizer_agent")
workflow.add_edge("risk_agent", "synthesizer_agent")
workflow.add_edge("synthesizer_agent", END)

# checkpointer = PostgresSaver(conn)
# checkpointer.setup()

# workflow = workflow.compile(
#     checkpointer=checkpointer,
# )
workflow = workflow.compile()
 
if __name__=='__main__':
    response = workflow.invoke({'messages': [HumanMessage(content='Apple revenue 2024')]})
    print(response)
