"""
NGO Proposal Drafting Bot - Streamlit Frontend
Week 1: Document upload + Basic Chat/Q&A interface

Run with: streamlit run frontend/app.py
"""
import streamlit as st
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="NGO Proposal Drafting Bot",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helper functions ────────────────────────────────────────────────────────────

def api_delete(endpoint: str) -> dict | None:
    """Make a DELETE request to the backend API."""
    try:
        resp = requests.delete(f"{API_BASE}{endpoint}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_get(endpoint: str) -> dict | None:
    """Make a GET request to the backend API."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(endpoint: str, json_data: dict = None, files=None) -> dict | None:
    """Make a POST request to the backend API."""
    try:
        if files:
            resp = requests.post(f"{API_BASE}{endpoint}", files=files, timeout=60)
        else:
            resp = requests.post(f"{API_BASE}{endpoint}", json=json_data, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def get_kb_stats() -> dict:
    """Fetch knowledge base statistics."""
    result = api_get("/documents/stats")
    return result or {"total_documents": 0, "total_chunks": 0, "collection_name": "N/A"}


# ── Sidebar ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/color/96/document--v1.png", width=60)
    st.title("NGO Proposal Bot")
    st.caption("PRJ-032 | Yeshwanth Sai R")
    st.divider()

    # Knowledge base stats
    st.subheader("📊 Knowledge Base")
    stats = get_kb_stats()
    col1, col2 = st.columns(2)
    col1.metric("Documents", stats.get("total_documents", 0))
    col2.metric("Chunks", stats.get("total_chunks", 0))

    st.divider()

    # Navigation
    st.subheader("Navigation")
    page = st.radio(
        "Go to",
        ["💬 Chat / Q&A", "📁 Upload Documents", "📋 Knowledge Base"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Week 1 Deliverable\nFastAPI + LangChain + ChromaDB + Streamlit")


# ── Page: Chat / Q&A ────────────────────────────────────────────────────────────

if page == "💬 Chat / Q&A":
    st.title("💬 Chat with NGO Knowledge Base")
    st.caption("Ask questions about NGO proposals, grant writing, and program design.")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Hello! I'm your NGO Proposal Drafting Assistant. 👋\n\n"
                "I can help you with:\n"
                "- **Grant proposal structure** and best practices\n"
                "- **Program design** and logical frameworks\n"
                "- **Budget planning** for NGO projects\n"
                "- **Donor requirements** and reporting standards\n\n"
                "Upload documents in the **Upload Documents** tab to get answers "
                "grounded in your specific NGO materials, or ask me anything about "
                "proposal writing!"
            ),
        })

    # Display chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Add action buttons for assistant messages
            if msg["role"] == "assistant":
                col1, col2, col3 = st.columns([1, 1, 10])
                
                with col1:
                    # Copy button
                    if st.button("📋", key=f"copy_{idx}", help="Copy to clipboard"):
                        st.code(msg["content"], language=None)
                        st.success("✓ Copied!", icon="✅")
                
                with col2:
                    # Regenerate button
                    if st.button("🔄", key=f"regen_{idx}", help="Regenerate response"):
                        # Find the user question that triggered this response
                        if idx > 0 and st.session_state.messages[idx-1]["role"] == "user":
                            user_question = st.session_state.messages[idx-1]["content"]
                            
                            # Remove this assistant message
                            st.session_state.messages.pop(idx)
                            
                            # Regenerate
                            with st.spinner("Regenerating..."):
                                result = api_post("/chat/ask", json_data={
                                    "question": user_question,
                                    "session_id": "streamlit_session",
                                })
                            
                            if result:
                                answer = result.get("answer", "Sorry, I could not generate an answer.")
                                sources = result.get("sources", [])
                                
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": answer,
                                    "sources": sources,
                                })
                            st.rerun()
                
                # Show sources as clickable links
                if msg.get("sources"):
                    with st.expander("📎 Sources"):
                        for src in msg["sources"]:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.caption(f"• {src}")
                            with col2:
                                if st.button("👁️ View", key=f"view_src_{idx}_{src}"):
                                    st.session_state["preview_doc"] = src
                                    st.session_state["show_doc_modal"] = True
                                    st.rerun()
            
            # Add edit button for user messages
            elif msg["role"] == "user":
                if st.button("✏️", key=f"edit_{idx}", help="Edit message"):
                    st.session_state[f"editing_{idx}"] = True
                    st.rerun()
                
                # Show edit input if editing
                if st.session_state.get(f"editing_{idx}", False):
                    edited_text = st.text_area(
                        "Edit your message:",
                        value=msg["content"],
                        key=f"edit_input_{idx}",
                        height=100
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save", key=f"save_{idx}"):
                            # Update the message
                            st.session_state.messages[idx]["content"] = edited_text
                            st.session_state[f"editing_{idx}"] = False
                            
                            # Remove all messages after this one
                            st.session_state.messages = st.session_state.messages[:idx+1]
                            
                            # Regenerate response
                            with st.spinner("Generating new response..."):
                                result = api_post("/chat/ask", json_data={
                                    "question": edited_text,
                                    "session_id": "streamlit_session",
                                })
                            
                            if result:
                                answer = result.get("answer", "Sorry, I could not generate an answer.")
                                sources = result.get("sources", [])
                                
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": answer,
                                    "sources": sources,
                                })
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()

    # Document preview modal (shown when source is clicked)
    if st.session_state.get("show_doc_modal") and st.session_state.get("preview_doc"):
        preview_doc = st.session_state["preview_doc"]
        st.divider()

        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(f"📖 {preview_doc}")
        with col2:
            if st.button("✖ Close", key="close_chat_preview"):
                st.session_state.pop("show_doc_modal", None)
                st.session_state.pop("preview_doc", None)
                st.rerun()

        with st.spinner("Loading document..."):
            preview_data = api_get(f"/documents/preview/{preview_doc}")

        if preview_data:
            c1, c2 = st.columns(2)
            c1.metric("Chunks", preview_data.get("total_chunks", 0))
            c2.metric("Characters", len(preview_data.get("content", "")))

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 20px;
                    height: 400px;
                    overflow-y: auto;
                    font-family: monospace;
                    font-size: 14px;
                    color: #ffffff;
                    white-space: pre-wrap;
                    line-height: 1.6;
                ">{preview_data.get("content", "").replace("<", "&lt;").replace(">", "&gt;")}</div>
                """,
                unsafe_allow_html=True,
            )

            st.download_button(
                label="⬇️ Download",
                data=preview_data.get("content", ""),
                file_name=preview_doc,
                mime="text/plain",
            )

    # Chat input
    if prompt := st.chat_input("Ask about NGO proposals, grant writing, or your uploaded documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get answer from API
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post("/chat/ask", json_data={
                    "question": prompt,
                    "session_id": "streamlit_session",
                })

            if result:
                answer = result.get("answer", "Sorry, I could not generate an answer.")
                sources = result.get("sources", [])

                st.markdown(answer)
                if sources:
                    with st.expander("📎 Sources"):
                        for src in sources:
                            st.caption(f"• {src}")

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

    # Clear chat button
    if st.session_state.messages and len(st.session_state.messages) > 1:
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.messages = []
            st.rerun()


# ── Page: Upload Documents ───────────────────────────────────────────────────────

elif page == "📁 Upload Documents":
    st.title("📁 Upload Documents to Knowledge Base")
    st.caption("Upload NGO documents, grant templates, or reference materials.")

    st.info(
        "**Supported formats:** PDF, TXT, DOCX  \n"
        "**Max file size:** 10MB  \n"
        "Documents are parsed, chunked, and stored in ChromaDB for semantic search."
    )

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "txt", "docx", "doc"],
        accept_multiple_files=True,
        help="You can upload multiple files at once",
    )

    if uploaded_files:
        if st.button("📤 Upload to Knowledge Base", type="primary"):
            progress = st.progress(0)
            results = []

            for i, uploaded_file in enumerate(uploaded_files):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    result = api_post("/documents/upload", files=files)

                    if result:
                        results.append(result)

                progress.progress((i + 1) / len(uploaded_files))

            progress.empty()

            # Show results
            if results:
                st.success(f"✅ Processed {len(results)} file(s) successfully!")
                for r in results:
                    st.write(f"• **{r['filename']}** → {r['chunks_created']} chunks created")
                st.rerun()

    st.divider()

    # Sample documents section
    st.subheader("📄 Load Sample Documents")
    st.caption("Don't have documents? Load pre-built NGO sample documents to test the system.")

    if st.button("📥 Load Sample NGO Documents", type="secondary"):
        sample_dir = Path("./data/sample_docs")
        sample_files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))

        if not sample_files:
            st.warning("No sample documents found. They will be created automatically.")
        else:
            loaded = 0
            for sample_file in sample_files:
                with open(sample_file, "rb") as f:
                    files = {"file": (sample_file.name, f.read(), "text/plain")}
                    result = api_post("/documents/upload", files=files)
                    if result:
                        loaded += 1
            if loaded:
                st.success(f"✅ Loaded {loaded} sample document(s)!")
                st.rerun()


# ── Page: Knowledge Base ─────────────────────────────────────────────────────────

elif page == "📋 Knowledge Base":
    st.title("📋 Knowledge Base Status")

    # Stats cards
    stats = get_kb_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Documents", stats.get("total_documents", 0))
    col2.metric("🧩 Chunks", stats.get("total_chunks", 0))
    col3.metric("🗄️ Collection", stats.get("collection_name", "N/A"))

    st.divider()

    # Document list
    st.subheader("Indexed Documents")
    doc_list = api_get("/documents/list")

    if doc_list and doc_list.get("documents"):
        for doc in doc_list["documents"]:
            col1, col2 = st.columns([4, 1])
            with col1:
                # Clickable document name — opens preview
                if st.button(f"📄 {doc}", key=f"preview_{doc}", help="Click to preview document"):
                    st.session_state["preview_doc"] = doc
            with col2:
                if st.button("🗑️", key=f"delete_{doc}", help=f"Delete {doc}"):
                    with st.spinner(f"Deleting {doc}..."):
                        result = api_delete(f"/documents/delete/{doc}")
                        if result:
                            # Clear preview if deleted doc was open
                            if st.session_state.get("preview_doc") == doc:
                                st.session_state.pop("preview_doc", None)
                            st.success(f"Deleted '{doc}'")
                            st.rerun()

        # Document preview panel
        if st.session_state.get("preview_doc"):
            preview_doc = st.session_state["preview_doc"]
            st.divider()

            # Header with close button
            col1, col2 = st.columns([5, 1])
            with col1:
                st.subheader(f"📖 {preview_doc}")
            with col2:
                if st.button("✖ Close", key="close_preview"):
                    st.session_state.pop("preview_doc", None)
                    st.rerun()

            # Fetch document content
            with st.spinner("Loading document..."):
                preview_data = api_get(f"/documents/preview/{preview_doc}")

            if preview_data:
                # Stats row
                c1, c2 = st.columns(2)
                c1.metric("Chunks", preview_data.get("total_chunks", 0))
                c2.metric("Characters", len(preview_data.get("content", "")))

                # Full content in scrollable box
                st.markdown(
                    f"""
                    <div style="
                        background-color: #1e1e1e;
                        border: 1px solid #444;
                        border-radius: 8px;
                        padding: 20px;
                        height: 400px;
                        overflow-y: auto;
                        font-family: monospace;
                        font-size: 14px;
                        color: #ffffff;
                        white-space: pre-wrap;
                        line-height: 1.6;
                    ">{preview_data.get("content", "").replace("<", "&lt;").replace(">", "&gt;")}</div>
                    """,
                    unsafe_allow_html=True,
                )

                # Download button
                st.download_button(
                    label="⬇️ Download Content",
                    data=preview_data.get("content", ""),
                    file_name=preview_doc,
                    mime="text/plain",
                )
    else:
        st.info("No documents in the knowledge base yet. Go to **Upload Documents** to add some.")

    st.divider()

    # Danger zone
    with st.expander("⚠️ Danger Zone"):
        st.warning("Clearing the knowledge base will remove all indexed documents. This cannot be undone.")
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            result = api_post("/documents/clear")
            if result:
                st.success("Knowledge base cleared.")
                st.rerun()
