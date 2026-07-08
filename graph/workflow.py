from langgraph.graph import StateGraph, START, END
from .state import GraphState
from nodes.query_decompose import QueryDecompose
from nodes.constructDB import Construct_DB

workflow = StateGraph(GraphState)
construct_db = Construct_DB()

#Node Defintions
workflow.add_node("constructdb", construct_db.build_vectordb)
workflow.add_node("query_decompose", QueryDecompose)

#Edge Defintion
workflow.add_edge(START, "query_decompose")
workflow.add_edge("query_decompose", "constructdb")
workflow.add_edge("constructdb", END)

workflow = workflow.compile()
