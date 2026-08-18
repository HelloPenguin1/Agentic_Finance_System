from vectordb.vectorstore import get_vectorstore
from config.llm_gateway import generate_llm_findings
from prompts.worker_prompts2 import (
    revenue_prompt,
    profitability_prompt,
    liquidity_prompt,
    risk_prompt,
    management_prompt,
)
from prompts.specific_prompt import SPECIFIC_PROMPT
from utils.reranker import build_context, rerank_documents

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    def __init__(self, config, prompt, state):
        self.vectorstore = get_vectorstore()

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
        logger.info(
        f"Collection count before retrieval: "
        f"{self.vectorstore._collection.count()}"
        )

        logger.info(f"Retrieval query: {self.retrieval_query}")
        logger.info(f"Filter: {self.build_filter()}")
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": self.k,
                "filter": self.build_filter(), #for metadata filtering
            }
        )

        docs = retriever.invoke(self.retrieval_query)  #pass the retrieval query here to get the documents 
        
        #DEBUG STATEMENT
        logger.info(f"Retriever returned {len(docs)} docs")

        for doc in docs[:3]:
            logger.info(doc.metadata)
        #END DEBUG STATEMENT
    
        docs = rerank_documents(
            query = self.retrieval_query,
            docs = docs,
            top_k = 5
        )
        logger.info(f"After reranking: {len(docs)} docs")
        
        context = build_context(docs)        
        logger.info(f"Context length: {len(context)}")
        
        return context

    async def generate_findings(self, context, state):
        #Generation only
        logger.info("Sending context to LLM")
        logger.info(context[:1000])
        
        output = await generate_llm_findings(
            user_query=state["messages"][-1].content,
            context=context,
            company=self.company,
            section_prompt=self.prompt,
        )

        return output


async def run_worker(worker_name: str, state):
    config = WORKER_CONFIG[worker_name]
    
    if state['intent']=='report':
        prompt = REPORT_PROMPTS[worker_name]  #return base answers 
    else:
        prompt = SPECIFIC_PROMPT
        
    agent = WorkerAgent(
        config=config, #sets up filters for k-values and sections to retrieve
        prompt=prompt, 
        state=state,
    )

    context = agent.retrieve(state)
    
    output = await agent.generate_findings(context, state)
    

    return {
        "retrieved_docs": context,
        "completed_sections": [
            {
                #"findings": output.findings, #internally contains citations and claims
                'findings':[f.model_dump() for f in output.findings]
            }
        ],
    }


async def revenue_agent(state):
    return await run_worker("revenue_agent", state)


async def profitability_agent(state):
    return await run_worker("profitability_agent", state)


async def liquidity_agent(state):
    return await run_worker("liquidity_agent", state)


async def risk_agent(state):
    return await run_worker("risk_agent",state)


async def management_agent(state):
    return await run_worker("management_agent", state)