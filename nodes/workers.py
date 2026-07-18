from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_section
from prompts.worker_prompts import revenue_prompt, profitability_prompt, liquidity_prompt, risk_prompt, management_prompt


WORKER_CONFIG = {
    "revenue_agent": {
        "k": 5,  # Sightly increased to capture both narrative and dense tables
        "retrieval_query": (
            "revenue recognition segment revenue sales breakdown products services "
            "operating results disaggregated revenue revenue from contracts with customers"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {
                    "section": {
                        "$in": [
                            "Item 7",          # 10-K MD&A
                            "Item 8",          # 10-K Financial Statements & Footnotes
                            "Part I, Item 2",  # 10-Q MD&A
                            "Part I, Item 1",  # 10-Q Financial Statements & Footnotes
                        ]
                    }
                },
                {"source": "SEC"},
                #{"filing_date": },
            ]
        },
    },

    "profitability_agent": {
        "k": 5,
        "retrieval_query": (
            "gross profit margin operating income net income earnings per share EPS "
            "cost of sales operating expenses selling general administrative SG&A"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {
                    "section": {
                        "$in": [
                            "Item 7",          # 10-K MD&A
                            "Item 8",          # 10-K Income Statement / Footnotes
                            "Part I, Item 2",  # 10-Q MD&A
                            "Part I, Item 1",  # 10-Q Income Statement
                        ]
                    }
                },
                {"source": "SEC"},
            ]
        },
    },

    "liquidity_agent": {
        "k": 5,
        "retrieval_query": (
            "cash equivalents liquidity working capital operating investing financing activities "
            "cash flows capital expenditures CapEx debt obligations credit facility share repurchases"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {
                    "section": {
                        "$in": [
                            "Item 7",          # 10-K MD&A (Capital Resources)
                            "Item 8",          # 10-K Statement of Cash Flows
                            "Part I, Item 2",  # 10-Q MD&A
                            "Part I, Item 1",  # 10-Q Statement of Cash Flows
                        ]
                    }
                },
                {"source": "SEC"},
            ]
        },
    },

    "risk_agent": {
        "k": 5,
        "retrieval_query": (
            "risk factors competition regulatory litigation legal proceedings supply chain "
            "cybersecurity macroeconomic headwinds concentration customer dependence"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {
                    "section": {
                        "$in": [
                            "Item 1A",         # 10-K Risk Factors
                            "Item 3",          # 10-K Legal Proceedings
                            "Part II, Item 1A",# 10-Q Risk Factors
                            "Part II, Item 1", # 10-Q Legal Proceedings
                        ]
                    }
                },
                {"source": "SEC"},
            ]
        },
    },

    "management_agent": {
        "k": 5,
        "retrieval_query": (
            "business outlook trends uncertainties management strategy growth initiatives "
            "long term goals restructuring integration execution plans"
        ),
        "filter": {
            "$and": [
                {"form": {"$in": ["10-K", "10-Q"]}},
                {
                    "section": {
                        "$in": [
                            "Item 7",          # 10-K MD&A Outlook
                            "Part I, Item 2",  # 10-Q MD&A Outlook
                        ]
                    }
                },
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
        }]
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