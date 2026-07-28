"""Streamlit frontend for the Agentic SEC Filing Analysis Assistant."""

import os
import requests
import streamlit as st

BACKEND_URL = "https://fin-agentic-assistant-370180169657.asia-south1.run.app"
TIMEOUT = 300


# ---------------------------------------------------------------------------
# Page config & session state
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Agentic SEC Filing Analysis Assistant",
    page_icon="📄",
    layout="centered",
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

    # Clear vector database
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

st.title("Agentic SEC Filing Analysis Assistant")
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
                st.write("Calling:", f"{BACKEND_URL}/ingest")
                resp = requests.post(
                    f"{BACKEND_URL}/ingest",
                    json={"company": company.strip(), 
                          "filing_year": int(filing_year)},
                    timeout=TIMEOUT,
                )
                st.write(resp.status_code)
                st.write(resp.text)
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
