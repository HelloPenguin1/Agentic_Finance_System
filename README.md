# Agentic Financial Intelligence Platform

An agentic, multi-agent orchestrated Retrieval-Augmented Generation (RAG) platform for analyzing SEC EDGAR filings. The system automates document ingestion, semantic indexing, intelligent retrieval, and coordinated financial reasoning to generate citation-grounded insights from official regulatory disclosures.

---

## Overview

Traditional financial research requires manually navigating lengthy SEC filings to locate relevant information. This platform streamlines that process by combining semantic search with a team of specialized AI agents capable of analyzing different aspects of a company's financial health.

The application retrieves SEC filings directly from EDGAR, converts them into vector embeddings, stores them in a vector database, and answers user queries by retrieving relevant evidence before synthesizing a final response backed by citations.

---

## Features

- Multi-agent orchestration using LangGraph
- Retrieval-Augmented Generation (RAG)
- SEC EDGAR filing ingestion
- Semantic vector search with ChromaDB
- Cross-encoder reranking for improved retrieval quality
- Citation-grounded responses from official SEC filings
- Financial report generation across multiple business dimensions
- REST API built with FastAPI
- Streamlit frontend
- Dockerized deployment on Google Cloud Run

---

# Architecture

```
                     User Query
                          │
                          ▼
                Planning / Query Decomposer
                          │
        Extract:
        • Company
        • Intent
        • Filing Sections
        • Date Range
                          │
                          ▼
                  Retrieval Pipeline
          (Vector Search + Reranking)
                          │
                          ▼
               Multi-Agent Orchestrator
                          │
        ┌────────┬────────┬────────┬────────┬────────┐
        ▼        ▼        ▼        ▼        ▼
    Revenue  Profit.  Liquidity   Risk   Management
      Agent    Agent     Agent    Agent     Agent
        └────────┴────────┴────────┴────────┴────────┘
                          │
                          ▼
                 Synthesizer Agent
                          │
                          ▼
             Citation-Grounded Response
```

---

# Agentic Workflow

Instead of relying on a single LLM prompt, the platform decomposes user requests into specialized tasks.

1. User submits a financial research query.
2. A planning agent extracts entities such as the company, intent, filing sections, and date range.
3. Relevant SEC filings are retrieved from the semantic vector database.
4. The orchestrator dynamically routes the task to one or more specialized financial agents.
5. Each agent analyzes only the relevant document context for its financial domain.
6. The synthesizer combines the individual findings into a unified response with citations to the source filings.

This modular architecture improves scalability, reasoning quality, and maintainability compared to a single-agent RAG pipeline.

---

# Retrieval Pipeline

SEC Filing

→ Document Chunking

→ Embedding Generation

→ Chroma Vector Database

→ Semantic Retrieval

→ Cross-Encoder Reranking

→ Specialized Financial Agents

→ Response Synthesis

---

# Technology Stack

## Backend

- Python
- FastAPI
- LangGraph
- LangChain

## Inference
Groq

## Vector Database

- ChromaDB

## Frontend

- Streamlit

## Deployment

- Docker
- Google Cloud Run
- Streamlit Community Cloud

---

# Current Database Design (IMP)

The current implementation uses a **local persistent ChromaDB directory** mounted within the Cloud Run container.

This design was intentionally chosen to keep deployment lightweight and simplify the demonstration of the retrieval pipeline.

Because the application currently runs on a **single Cloud Run instance**, all users share the same vector database.

As a result:

- The vector database is shared across all users.
- Ingested filings are stored in the same Chroma collection.
- The **Clear Vector Database** operation clears the shared collection.
- The application is currently intended as a demonstration and portfolio project rather than a multi-tenant production deployment.


# Planned Improvement

The next major update is migrating from the local ChromaDB deployment to **Pinecone**.

This migration will provide:

- Cloud-hosted vector storage
- Better scalability
- Improved persistence
- True multi-user isolation
- Production-ready deployment architecture

Future releases will also incorporate authentication and namespace-based retrieval so each user's indexed documents remain isolated from others.


# Example Queries

- What risks did NVIDIA identify in its latest 10-K filing?
- Analyze Microsoft's liquidity position.
- Go over some of Amazon's profitability trends.
- Summarize management's discussion and outlook.

---

# Future Roadmap

- Pinecone vector database migration
- Conversation memory
- Access to numeric data tables
