from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_section
from prompts.worker_prompts import (
    revenue_prompt,
    profitability_prompt,
    liquidity_prompt,
    risk_prompt,
    management_prompt,
)
from prompts.specific_prompt import SPECIFIC_PROMPT

WORKER_CONFIG = {
    "revenue_agent": {
        "k": 3,
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "profitability_agent": {
        "k": 3,
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "liquidity_agent": {
        "k": 3,
        
        
        "forms": ["10-K", "10-Q"],
        "sections": [
            "Item 7",
            "Item 8",
            "Part I, Item 2",
            "Part I, Item 1",
        ],
    },

    "risk_agent": {
        "k": 3,
        "forms": ["10-K", "10-Q"],
        
        "sections": [
            "Item 1A",
            "Item 3",
            "Part II, Item 1A",
            "Part II, Item 1",
        ],
    },

    "management_agent": {
        "k": 3,
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
        self.start_year = int(state["start_year"])
        self.end_year = (
            int(state["end_year"])
            if state["end_year"] is not None
            else self.start_year
        )

        #for answer generation
        self.prompt = prompt
        self.company = state["company"]
        
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

    def retrieve(self, state):
        #Retrieval Generation
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": self.k,
                "filter": self.build_filter(), #for metadata filtering
            }
        )

        docs = retriever.invoke(self.retrieval_query)  #pass the retrieval query here to get the documents 

        context = [{
            "chunk_id":d.metadata["chunk_id"],
            "form": d.metadata["form"],
            "section":d.metadata["section"],
            "accession_number":d.metadata["accession_number"],
            "doc": d.page_content
        } for d in docs]
        
        return context
     
    
    def generate(self, context, state):
        #Generation only 
        output = generate_section(
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
    
    output = agent.generate(context, state)
    

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