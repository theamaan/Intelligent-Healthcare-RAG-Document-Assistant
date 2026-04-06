import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Healthcare RAG Assistant", layout="wide")
st.title("Intelligent Healthcare Document Assistant")
st.caption("Upload insurance or medical documents and ask grounded questions with citations.")

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None

with st.sidebar:
    st.subheader("Upload Document")
    upload_file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"])
    if upload_file and st.button("Index Document", type="primary"):
        with st.spinner("Uploading and indexing..."):
            files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
            response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=300)
            if response.ok:
                payload = response.json()
                st.session_state.doc_id = payload["doc_id"]
                st.success(f"Indexed {payload['filename']} into {payload['chunk_count']} chunks")
            else:
                st.error(response.text)

    st.subheader("Active Document")
    st.write(st.session_state.doc_id or "No document indexed yet")

if st.session_state.doc_id:
    question = st.text_input("Ask a question", placeholder="Is hospitalization covered?")
    if st.button("Ask") and question.strip():
        with st.spinner("Retrieving and generating answer..."):
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"doc_id": st.session_state.doc_id, "question": question},
                timeout=180,
            )
            if not response.ok:
                st.error(response.text)
            else:
                payload = response.json()
                st.subheader("Answer")
                st.write(payload["answer"])
                st.progress(payload["confidence"])
                st.caption(f"Confidence proxy: {payload['confidence']:.2f}")

                st.subheader("Citations")
                if payload["citations"]:
                    for citation in payload["citations"]:
                        page = citation["page_number"] if citation["page_number"] is not None else "N/A"
                        st.markdown(
                            f"- **{citation['source']}** | Page: {page} | Chunk: {citation['chunk_index']}\n"
                            f"  > {citation['excerpt']}..."
                        )
                else:
                    st.info("No citations returned for this answer.")

                history_resp = requests.get(f"{API_BASE_URL}/history/{st.session_state.doc_id}", timeout=60)
                if history_resp.ok:
                    st.subheader("Recent History")
                    for item in history_resp.json().get("items", [])[-5:][::-1]:
                        st.write(f"Q: {item['question']}")
                        st.write(f"A: {item['answer']}")
                        st.caption(item["timestamp"])
else:
    st.info("Upload and index a document to begin querying.")
