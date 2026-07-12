from langgraph.graph import StateGraph, START, END
from .state import GraphState
from nodes.query_decompose import QueryDecompose
from nodes.constructDB import Construct_DB
from nodes.workers import revenue_agent, profitability_agent
from nodes.assign_workers import assign_workers

workflow = StateGraph(GraphState)
construct_db = Construct_DB()

#Node Defintions
workflow.add_node("constructdb", construct_db.build_vectordb)
workflow.add_node("query_decompose", QueryDecompose)
workflow.add_node("revenue_agent", revenue_agent)
workflow.add_node("profitability_agent", profitability_agent)



#Edge Defintion
workflow.add_edge(START, "query_decompose")
workflow.add_edge("query_decompose", "constructdb")
workflow.add_conditional_edges("constructdb", 
                               assign_workers,
                               ["revenue_agent",
                              ]) #routing function
                               
workflow.add_edge("revenue_agent", END)


workflow = workflow.compile()


# needs work here