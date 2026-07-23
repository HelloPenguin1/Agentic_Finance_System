from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_llm_findings
from prompts.worker_prompts import (
    revenue_prompt,
    profitability_prompt,
    liquidity_prompt,
    risk_prompt,
    management_prompt,
)
from prompts.specific_prompt import SPECIFIC_PROMPT
from utils.reranker import build_context, rerank_documents

WORKER_CONFIG = {
    "revenue_agent": {
        "k": 20,
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "profitability_agent": {
        "k": 20,
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "liquidity_agent": {
        "k": 20,
        
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "risk_agent": {
        "k": 20,
        "forms": ["10-K", "10-Q"],
        
        "sections": [
            "Item 1A",
            "Item 3",
            "Part II, Item 1A",
            "Part II, Item 1",
        ],
    },

    "management_agent": {
        "k": 20,
        "forms": ["10-K", "10-Q"],
        
        "sections": [
            "Item 7",
            "Part I, Item 2",
        ],
    },
}

REPORT_PROMPTS = {
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
        self.retrieval_query = state["optimized_query"]  #retriever only sees this
        
        #Arguments for retriever/build filter
        self.k = config["k"]
        self.forms = config["forms"]
        self.sections = config["sections"]

        # Keep retrieval simple and consistent with ingestion.
        # The query decomposer may provide year hints, but they are not used
        # for metadata filtering here to avoid mismatches after ingestion.
        self.prompt = prompt
        self.company = state["company"]
        
    def build_filter(self):
        return {
            "$and": [
                {"ticker": self.company},
                {"form": {"$in": self.forms}},
                {"section": {"$in": self.sections}},
                {"source": "SEC"},
            ]
        }

    def retrieve(self, state):
        #Retrieval Generation
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": self.k,
                "filter": self.build_filter(), #for metadata filtering
            }
        )

        docs = retriever.invoke(self.retrieval_query)  #pass the retrieval query here to get the documents 

        docs = rerank_documents(
            query = self.retrieval_query,
            docs = docs,
            top_k = 5
        )
        context = build_context(docs)        
        
        return context

    def generate_findings(self, context, state):
        #Generation only
        output = generate_llm_findings(
            user_query=state["messages"][-1].content,
            context=context,
            section=self.section_name,
            company=self.company,
            section_prompt=self.prompt,
        )

        return output


def run_worker(worker_name: str, section_name: str, state):
    config = WORKER_CONFIG[worker_name]
    
    if state['intent']=='report':
        prompt = REPORT_PROMPTS[worker_name]  #return base answers 
    else:
        prompt = SPECIFIC_PROMPT
        
    agent = WorkerAgent(
        section_name=section_name,
        config=config, #sets up filters for k-values and sections to retrieve
        prompt=prompt, 
        state=state,
    )

    context = agent.retrieve(state)
    
    output = agent.generate_findings(context, state)
    

    return {
        "retrieved_docs": context,
        "completed_sections": [
            {
                "section": output.section,
                "findings": output.findings, #internally contains citations and claims
            }
        ],
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