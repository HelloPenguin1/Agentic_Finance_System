from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_section
from prompts.worker_prompts import revenue_prompt, profitability_prompt, liquidity_prompt, risk_prompt, management_prompt


WORKER_CONFIG = {

    "revenue_agent": {
        "k": 4,
        "retrieval_query": (
            "revenue growth segment revenue sales products "
            "services operating results guidance"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {"section": {"$in": ["Item 7", "Item 2"]}},
                {"source": "SEC"},
            ]
        },
    },

    "profitability_agent": {
        "k": 6,
        "retrieval_query": (
            "gross margin operating margin net income "
            "profit earnings cost of revenue operating expenses"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {"section": {"$in": ["Item 7", "Item 8", "Item 1"]}},
                {"source": "SEC"},
            ]
        },
    },

    "liquidity_agent": {
        "k": 5,
        "retrieval_query": (
            "cash liquidity capital resources debt "
            "cash flow financing investing operating activities"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {"section": {"$in": ["Item 7", "Item 2"]}},
                {"source": "SEC"},
            ]
        },
    },

    "risk_agent": {
        "k": 5,
        "retrieval_query": (
            "risk competition regulation litigation "
            "supply chain cybersecurity macroeconomic"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {"section": {"$in": ["Item 1A", "Item 3"]}},
                {"source": "SEC"},
            ]
        },
    },

    "management_agent": {
        "k": 5,
        "retrieval_query": (
            "management strategy outlook guidance "
            "future expectations priorities investments"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {"section": {"$in": ["Item 7", "Item 2"]}},
                {"source": "SEC"},
            ]
        },
    },
}

PROMPTS = {
    "revenue_agent": revenue_prompt,
    "profitability_agent": profitability_prompt,
    "liquidity_agent": liquidity_prompt,
    "risk_agent": risk_prompt,
    "management_agent": management_prompt,
}


class WorkerAgent:
    def __init__(self, section_name, query, k, filter, prompt, state):
        self.vectorstore = get_vectorstore()
        self.section_name = section_name
        self.query = query
        self.k = k
        self.filter = filter
        self.prompt = prompt
        self.company = state.get("company", "Unknown Company")

    def retrieve_and_generate(self) -> str:
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": self.k,
                "filter": self.filter,
            }
        )
        docs = retriever.invoke(self.query)
        context = "\n\n".join([d.page_content for d in docs])
        output = generate_section(
            context=context,
            section=self.section_name,
            company=self.company,
            section_prompt=self.prompt,
        )
        return output
    

def run_worker(worker_name: str, section_name: str, state):
    config = WORKER_CONFIG[worker_name]

    agent = WorkerAgent(
        section_name=section_name,
        query=config["retrieval_query"],
        k=config["k"],
        filter=config["filter"],
        prompt=PROMPTS[worker_name],
        state=state,
    )

    output = agent.retrieve_and_generate()

    return {
        "completed_sections": [{
            "section": output.heading,
            "content": output.content,
        }
    ]
}


def revenue_agent(state):
    return run_worker("revenue_agent", "revenue", state)

def profitability_agent(state):
    return run_worker("profitability_agent", "profitability", state)

def liquidity_agent(state):
    return run_worker("liquidity_agent", "liquidity", state)

def risk_agent(state):
    return run_worker("risk_agent", "risk", state)

def management_agent(state):
    return run_worker("management_agent", "management", state)