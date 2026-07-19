from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_section
from prompts.worker_prompts import (
    revenue_prompt,
    profitability_prompt,
    liquidity_prompt,
    risk_prompt,
    management_prompt,
)

WORKER_CONFIG = {
    "revenue_agent": {
        "k": 5,
        "retrieval_query": (
            "revenue recognition segment revenue sales breakdown products services "
            "operating results disaggregated revenue revenue from contracts with customers"
        ),
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "profitability_agent": {
        "k": 5,
        "retrieval_query": (
            "gross profit margin operating income net income earnings per share EPS "
            "cost of sales operating expenses selling general administrative SG&A"
        ),
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "liquidity_agent": {
        "k": 5,
        "retrieval_query": (
            "cash equivalents liquidity working capital operating investing financing activities "
            "cash flows capital expenditures CapEx debt obligations credit facility share repurchases"
        ),
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "risk_agent": {
        "k": 5,
        "retrieval_query": (
            "risk factors competition regulatory litigation legal proceedings supply chain "
            "cybersecurity macroeconomic headwinds concentration customer dependence"
        ),
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 1A",
            "Item 3",
            "Part II, Item 1A",
            "Part II, Item 1",
        ],
    },

    "management_agent": {
        "k": 5,
        "retrieval_query": (
            "business outlook trends uncertainties management strategy growth initiatives "
            "long term goals restructuring integration execution plans"
        ),
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Part I, Item 2",
        ],
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
    def __init__(self, section_name, config, prompt, state):
        self.vectorstore = get_vectorstore()

        self.section_name = section_name
        self.query = config["retrieval_query"]
        self.k = config["k"]
        self.forms = config["forms"]
        self.sections = config["sections"]

        self.prompt = prompt

        self.company = state["company"]
        self.start_year = int(state["start_year"])
        self.end_year = (
            int(state["end_year"])
            if state["end_year"] is not None
            else self.start_year
        )

    def build_filter(self):
        filters = [
            {"ticker": self.company},
            {"form": {"$in": self.forms}},
            {"section": {"$in": self.sections}},
            {"source": "SEC"},
        ]

        if self.start_year == self.end_year:
            filters.append(
                {"filing_year": self.start_year}
            )
        else:
            filters.append(
                {
                    "filing_year": {
                        "$gte": self.start_year,
                        "$lte": self.end_year,
                    }
                }
            )

        return {"$and": filters}

    def retrieve_and_generate(self):
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": self.k,
                "filter": self.build_filter(),
            }
        )

        docs = retriever.invoke(self.query)

        context = "\n\n".join(doc.page_content for doc in docs)

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
        config=config,
        prompt=PROMPTS[worker_name],
        state=state,
    )

    output = agent.retrieve_and_generate()

    return {
        "completed_sections": [
            {
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