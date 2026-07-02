from langgraph.graph import StateGraph, START, END
from .state import GraphState
from nodes.query_decompose import QueryDecompose


workflow = StateGraph(GraphState)

#Node Defintions
workflow.add_node("query_decompose", QueryDecompose)

#Edge Defintion
workflow.add_edge(START, "query_decompose")
workflow.add_edge("query_decompose", END)

workflow = workflow.compile()
