"""Streamlit frontend for the Agentic SEC Filing Analysis Assistant."""

import os
import requests
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL").rstrip("/")
TIMEOUT = 300


# ---------------------------------------------------------------------------
# Page config & session state
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Agentic Financial Research Assistant",
    page_icon="📈",
    layout="centered",
)

# Times New Roman font via a single scoped style injection
st.markdown(
    "<style>html, body, [class*='css'] { font-family: 'Times New Roman', Times, serif; }</style>",
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Settings")

    # Health check
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
        healthy = resp.json().get("status") == "healthy"
    except Exception:
        healthy = False

    if healthy:
        st.success("🟢 Connected")
    else:
        st.error("🔴 Backend unavailable")
    st.caption(f"**Backend URL:** `{BACKEND_URL}`")
    st.divider()

    # About SEC filings
    st.markdown(
        """
        **About SEC Filings**

        SEC filings are official financial and regulatory reports that public companies
        submit to the U.S. Securities and Exchange Commission (SEC).
        """
    )
    st.divider()

    # Endpoint descriptions
    st.markdown("**Endpoint Reference**")

    with st.expander("Ingest Filings"):
        st.write(
            "Retrieves SEC filings for the selected company, splits them into chunks, "
            "generates embeddings, and stores them in the vector database for semantic search."
        )

    with st.expander("Query"):
        st.write(
            "Searches the vector database for relevant filing sections and uses multiple retrieval"
            "agents as needed to generate evidence-based answers grounded in SEC documents."
        )

    with st.expander("Clear Vector Database"):
        st.write(
            "Deletes all indexed filing embeddings from the vector database, "
            "allowing a fresh ingestion of new documents."
        )

    st.divider()

    # Clear vector database action
    st.subheader("Vector Database")
    if st.button("🗑️ Clear Vector Database", use_container_width=True):
        st.session_state.confirm_clear = True

    if st.session_state.get("confirm_clear"):
        st.warning("This will permanently delete all indexed data. Are you sure?")
        col_yes, col_no = st.columns(2)
        if col_yes.button("Yes, clear", type="primary", use_container_width=True):
            try:
                resp = requests.post(f"{BACKEND_URL}/clear_vectorstore", timeout=TIMEOUT)
                resp.raise_for_status()
                st.success(resp.json().get("message", "Cleared."))
            except Exception as e:
                st.error(str(e))
            finally:
                st.session_state.confirm_clear = False
        if col_no.button("Cancel", use_container_width=True):
            st.session_state.confirm_clear = False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

st.title("Agentic Financial Research Assistant")
st.markdown(
    """
    A multi-agent orchestrated financial research platform built on Retrieval-Augmented Generation (RAG). \
        The system ingests SEC EDGAR filings, constructs a semantic vector index, decomposes user queries, 
        dynamically routes tasks to specialized financial agents, and synthesizes evidence-backed analyses 
        with traceable citations.
    """
)
st.divider()


# Section 1 — Ingest
st.header("1. Ingest SEC Filings")

with st.form("ingest_form"):
    company = st.text_input("Company Name", placeholder="e.g. Apple Inc.")
    filing_year = st.number_input("Filing Year", min_value=1993, max_value=2100, value=2023, step=1, format="%d")
    submitted = st.form_submit_button("Ingest Filings", use_container_width=True)

if submitted:
    if not company.strip():
        st.error("Please enter a company name.")
    else:
        with st.spinner(f"Ingesting filings for **{company.strip()}** ({int(filing_year)})…"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/ingest",
                    json={"company": company.strip(), "filing_year": int(filing_year)},
                    timeout=TIMEOUT,
                )
                resp.raise_for_status()
                data = resp.json()
                st.success(f"✅ {data.get('message', 'Ingestion completed.')}")
                st.info(f"**Chunks indexed:** {data.get('chunks_indexed', 'N/A')}")
            except Exception as e:
                st.error(str(e))


st.divider()


# Section 2 — Ask Questions
st.header("2. Ask Questions")

# Render chat history
for turn in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        citations = turn.get("citations", [])
        if citations:
            with st.expander("Sources"):
                for cite in citations:
                    parts = []
                    if cite.get("form"):
                        parts.append(f"**Filing:** {cite['form']}")
                    if cite.get("section"):
                        parts.append(f"**Section:** {cite['section']}")
                    if cite.get("accession_number"):
                        parts.append(f"**Accession #:** `{cite['accession_number']}`")
                    st.markdown(" · ".join(parts))

# Input
question = st.text_area("Your question", placeholder="e.g. What were Apple's main risk factors in 2023?", height=120, label_visibility="collapsed")

if st.button("Submit", disabled=not question.strip(), use_container_width=False):
    with st.spinner("Thinking…"):
        try:
            resp = requests.post(f"{BACKEND_URL}/query", json={"query": question.strip()}, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            st.session_state.chat_history.append({
                "question": question.strip(),
                "answer": data.get("answer", "No answer returned."),
                "citations": data.get("citations", []),
            })
        except Exception as e:
            st.session_state.chat_history.append({
                "question": question.strip(),
                "answer": f"Error: {e}",
                "citations": [],
            })
    st.rerun()
