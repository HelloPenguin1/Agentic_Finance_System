from graph.state import GraphState


def QueryDecompose(state):
    query = state["query"].lower()
    return {"requirement": "due_diligence_report"} if "due diligence" in query else {}
    
            