from config.llm_gateway import aggregate_findings

async def synthesizer_agent(state):
    latest_query = state['messages'][-1].content
    completed_sections = state['completed_sections']  
    output = await aggregate_findings(latest_query, completed_sections)

    return {
        'final_response': {
            'content': output.content,
            'citations': output.citations,
        }
    }

