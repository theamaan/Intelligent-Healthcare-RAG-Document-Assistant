import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Healthcare RAG Assistant", layout="wide")
st.title("Intelligent Healthcare Document Assistant")
st.caption("Upload insurance or medical documents and ask grounded questions with citations.")

# ── Session state init ────────────────────────────────────────────────────────
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "doc_info" not in st.session_state:
    st.session_state.doc_info = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Backend health check
    st.subheader("Backend Status")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health.ok:
            data = health.json()
            ollama_ok = data.get("ollama_connected", False)
            st.success("Backend: connected")
            if ollama_ok:
                st.success("Ollama: connected")
            else:
                st.warning("Ollama: not reachable — start Ollama and pull the model")
        else:
            st.error(f"Backend returned {health.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Backend: not reachable — start the API server first")

    st.divider()

    st.subheader("Upload Document")
    upload_file = st.file_uploader("PDF or DOCX (≤ 15 MB)", type=["pdf", "docx"])
    if upload_file and st.button("Index Document", type="primary"):
        with st.spinner("Uploading and indexing — this may take a minute..."):
            try:
                files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
                response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=300)
                if response.ok:
                    payload = response.json()
                    st.session_state.doc_id = payload["doc_id"]
                    st.session_state.doc_info = payload
                    st.success(
                        f"Indexed **{payload['filename']}** into **{payload['chunk_count']}** chunks"
                    )
                else:
                    st.error(f"Upload failed: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is the API server running?")

    st.divider()

    st.subheader("Active Document")
    if st.session_state.doc_info:
        info = st.session_state.doc_info
        st.markdown(f"**File:** {info['filename']}")
        st.markdown(f"**ID:** `{info['doc_id']}`")
        st.markdown(f"**Chunks:** {info['chunk_count']}")
    else:
        st.info("No document indexed yet.")

# ── Main area with tabs ───────────────────────────────────────────────────────
tab_chat, tab_eval = st.tabs(["Chat", "Evaluation"])

# ── Chat tab ──────────────────────────────────────────────────────────────────
with tab_chat:
    if st.session_state.doc_id:
        question = st.text_input(
            "Ask a question about the document",
            placeholder="Is hospitalization covered?",
        )
        if st.button("Ask", type="primary") and question.strip():
            with st.spinner("Retrieving context and generating answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"doc_id": st.session_state.doc_id, "question": question},
                        timeout=180,
                    )
                    if not response.ok:
                        st.error(f"Query failed: {response.text}")
                    else:
                        payload = response.json()

                        st.subheader("Answer")
                        st.write(payload["answer"])

                        confidence = payload["confidence"]
                        st.progress(confidence)
                        st.caption(
                            f"Confidence proxy: {confidence:.2f}  "
                            f"(based on number of supporting chunks retrieved)"
                        )

                        st.subheader("Citations")
                        if payload["citations"]:
                            for citation in payload["citations"]:
                                page = (
                                    citation["page_number"]
                                    if citation["page_number"] is not None
                                    else "N/A"
                                )
                                st.markdown(
                                    f"- **{citation['source']}** | "
                                    f"Page: {page} | Chunk: {citation['chunk_index']}\n"
                                    f"  > {citation['excerpt']}..."
                                )
                        else:
                            st.info("No citations returned for this answer.")

                        # Refresh history
                        history_resp = requests.get(
                            f"{API_BASE_URL}/history/{st.session_state.doc_id}",
                            timeout=60,
                        )
                        if history_resp.ok:
                            items = history_resp.json().get("items", [])
                            if items:
                                st.subheader("Recent History (latest 5)")
                                for item in items[-5:][::-1]:
                                    with st.expander(f"Q: {item['question'][:80]}"):
                                        st.write(item["answer"])
                                        st.caption(item["timestamp"])
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend. Is the API server running?")
    else:
        st.info("Upload and index a document using the sidebar to begin querying.")

# ── Evaluation tab ────────────────────────────────────────────────────────────
with tab_eval:
    st.subheader("RAGAS Evaluation Results")
    st.markdown(
        "Run the evaluation script to generate a report, then view the latest results here.\n\n"
        "```bash\npython -m backend.app.evaluation.ragas_eval\n```"
    )
    if st.button("Load Latest Evaluation Report"):
        with st.spinner("Fetching evaluation results..."):
            try:
                resp = requests.get(f"{API_BASE_URL}/eval/latest", timeout=30)
                if resp.ok:
                    data = resp.json()
                    st.success(f"Report: **{data['filename']}**")
                    results = data.get("results", {})
                    per_sample = results.get("per_sample", [])
                    if per_sample:
                        import pandas as pd

                        df = pd.DataFrame(per_sample)
                        # show numeric metric columns as a summary
                        metric_cols = [
                            c
                            for c in df.columns
                            if c
                            not in ("user_input", "response", "retrieved_contexts", "reference")
                        ]
                        if metric_cols:
                            st.subheader("Aggregate Scores")
                            summary = df[metric_cols].mean().reset_index()
                            summary.columns = ["Metric", "Mean Score"]
                            st.dataframe(summary, use_container_width=True)
                        st.subheader("Per-Sample Results")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.json(results)
                elif resp.status_code == 404:
                    st.warning(resp.json().get("detail", "No evaluation results found."))
                else:
                    st.error(f"Error: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is the API server running?")

