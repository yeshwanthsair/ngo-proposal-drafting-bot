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
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Sources"):
                    for src in msg["sources"]:
                        st.caption(f"• {src}")

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
            st.write(f"✅ {doc}")
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
