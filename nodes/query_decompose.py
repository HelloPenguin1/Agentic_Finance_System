from graph.state import GraphState
from config.llm_gateway import querydecomposer


def QueryDecompose(state: GraphState):
    """This node takes a user query and extracts entity infomration"""
    output = querydecomposer(state['query'])
    return {
        "company": output.company,
        "start_date": output.start_date,
        "end_date": output.end_date,
        "intent": output.intent
    }
    
            