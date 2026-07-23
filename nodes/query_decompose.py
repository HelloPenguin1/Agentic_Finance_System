from graph.state import GraphState
from config.llm_gateway import querydecomposer
from utils.resolve_c import resolve_company


def QueryDecompose(state: GraphState):
    """This node takes a user query and extracts entity infomration"""
    latest_query = state['messages'][-1].content  
    output = querydecomposer(latest_query)

    
    return {
        "company": resolve_company(output.company),
        "start_year": output.start_year,
        "end_year": output.end_year,
        "intent": output.intent,
        "requested_sections": output.requested_sections,
        "optimized_query": output.optimized_query
    }
    
            