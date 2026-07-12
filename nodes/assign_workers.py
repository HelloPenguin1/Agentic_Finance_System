from langgraph.types import Send
from graph.state import GraphState


WORKER_MAP = {
    "revenue": "revenue_agent", #agents to be made
    "profitability": "profitability_agent",
    "liquidity": "liquidity_agent",
    "risk": "risk_agent",
    "management": "management_agent",
}


def assign_workers(state: GraphState):

    return [
        Send(
            WORKER_MAP[section], #send to respective agents the state 
            state
        )
        for section in state["requested_sections"]
    ]