from graph.state import GraphState
from config.llm_gateway import querydecomposer
from tools.resolve_c import resolve_company


def QueryDecompose(state: GraphState):
    """This node takes a user query and extracts entity infomration"""
    output = querydecomposer(state['query'])
    all_sections = ["revenue", "profitability", "risk", "management", "liquidity"]
    
    #Set sections to 'all' workers if report is asked
    if output.intent=="report":
        output.requested_sections = all_sections
        
    return {
        "company": resolve_company(output.company),
        "start_year": output.start_year,
        "end_year": output.end_year,
        "intent": output.intent,
        "requested_sections": output.requested_sections
    }
    
            