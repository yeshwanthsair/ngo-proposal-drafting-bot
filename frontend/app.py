"""
NGO Proposal Drafting Bot - Streamlit Frontend (Standalone)
All backend services are imported directly - no FastAPI server needed.
Deploy this single file to Streamlit Cloud.
"""
import sys
import os
from pathlib import Path

# ── Add project root to path so backend imports work ─────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Import backend services directly ─────────────────────────────────────────
from backend.services.knowledge_base import get_knowledge_base
from backend.services.document_parser import chunk_text, parse_document
from backend.services.retrieval_service import retrieve_with_citations, handle_edge_cases
from backend.services.llm_service import answer_question, answer_without_kb, answer_with_memory
from backend.services.proposal_generator import generate_proposal_section, generate_checklist
from backend.services.chat_logger import log_interaction, get_chat_history, get_stats as get_log_stats, clear_history
from backend.services.session_manager import (
    get_session, create_session, add_to_conversation,
    get_conversation_history, clear_conversation,
    get_all_sessions, get_session_stats, verify_admin
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_current_timestamp() -> str:
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def format_timestamp_for_display(ts: str) -> str:
    if " at " in str(ts):
        return ts
    try:
        if 'T' in str(ts):
            clean = ts.split('+')[0].split('Z')[0]
            dt = datetime.fromisoformat(clean)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        return ts
    except Exception:
        return str(ts)[:19] if len(str(ts)) > 19 else str(ts)


@st.cache_resource(show_spinner=False)
def get_kb():
    """Cached knowledge base instance — loaded lazily, not at startup."""
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    from backend.services.knowledge_base import KnowledgeBase
    return KnowledgeBase(persist_dir=persist_dir)


def get_kb_stats_direct() -> dict:
    """Return stats WITHOUT triggering model load — fast for sidebar."""
    try:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        import chromadb
        client = chromadb.PersistentClient(path=persist_dir)
        try:
            collection = client.get_collection("ngo_knowledge_base")
            count = collection.count()
            if count > 0:
                results = collection.get(include=["metadatas"])
                sources = set()
                for meta in results.get("metadatas", []):
                    if meta and "source" in meta:
                        sources.add(meta["source"])
                return {"total_documents": len(sources), "total_chunks": count,
                        "collection_name": "ngo_knowledge_base", "documents": list(sources)}
        except Exception:
            pass
        return {"total_documents": 0, "total_chunks": 0,
                "collection_name": "ngo_knowledge_base", "documents": []}
    except Exception:
        return {"total_documents": 0, "total_chunks": 0, "collection_name": "N/A", "documents": []}


def ask_question_direct(question: str, session_id: str, use_memory: bool) -> dict:
    """Call backend services directly instead of HTTP."""
    try:
        kb = get_kb()
        stats = kb.get_stats()

        # Edge case check
        edge = handle_edge_cases(question, stats)
        if edge:
            return {"answer": edge, "sources": [], "citations": [], "chunks_used": 0,
                    "timestamp": get_current_timestamp()}

        # Retrieve context
        retrieval = retrieve_with_citations(question, kb, k=5)

        # Get conversation history if memory enabled
        if use_memory:
            history = get_conversation_history(session_id, last_n=6)
            result = answer_with_memory(question, retrieval, history)
        else:
            if retrieval["total_used"] > 0:
                result = answer_question(question, retrieval)
            else:
                result = answer_without_kb(question)

        # Save to memory
        add_to_conversation(session_id, "user", question)
        add_to_conversation(session_id, "assistant", result["answer"])

        # Log interaction
        log_interaction(
            session_id=session_id,
            question=question,
            answer=result["answer"],
            sources=result.get("sources", []),
            retrieval_info={"chunks_used": result.get("chunks_used", 0),
                            "citations": result.get("citations", [])},
        )

        result["timestamp"] = get_current_timestamp()
        return result

    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": [], "citations": [],
                "chunks_used": 0, "timestamp": get_current_timestamp()}


def upload_document_direct(filename: str, content: bytes) -> dict:
    """Parse and add document to knowledge base."""
    import tempfile
    try:
        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        raw_text = parse_document(tmp_path)
        os.unlink(tmp_path)

        if not raw_text.strip():
            return {"error": "No text found in document"}

        docs = chunk_text(raw_text, filename)
        kb = get_kb()
        kb.add_documents(docs)
        return {"filename": filename, "chunks_created": len(docs)}
    except Exception as e:
        return {"error": str(e)}


def generate_proposal_direct(data: dict, section: str) -> dict:
    """Generate proposal section directly."""
    from backend.services.llm_service import get_llm
    try:
        llm = get_llm()
        content = generate_proposal_section(section, data, llm)
        return {"content": content, "generated_at": get_current_timestamp()}
    except Exception as e:
        return {"error": str(e)}


def delete_document_direct(doc_name: str) -> dict:
    """Delete a document from knowledge base."""
    try:
        kb = get_kb()
        vs = kb._get_vector_store()
        collection = vs._collection
        results = collection.get(include=["metadatas"])
        ids_to_delete = []
        for i, meta in enumerate(results.get("metadatas", [])):
            if meta and meta.get("source") == doc_name:
                ids_to_delete.append(results["ids"][i])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            return {"deleted": doc_name, "chunks_removed": len(ids_to_delete)}
        return {"error": f"Document '{doc_name}' not found"}
    except Exception as e:
        return {"error": str(e)}


def clear_kb_direct() -> dict:
    """Clear entire knowledge base."""
    try:
        kb = get_kb()
        kb.delete_collection()
        # Reset cache
        st.cache_resource.clear()
        return {"message": "Knowledge base cleared"}
    except Exception as e:
        return {"error": str(e)}


def get_document_list_direct() -> dict:
    stats = get_kb_stats_direct()
    return {"documents": stats.get("documents", [])}


def get_document_preview_direct(doc_name: str) -> dict:
    try:
        kb = get_kb()
        vs = kb._get_vector_store()
        collection = vs._collection
        results = collection.get(include=["documents", "metadatas"])
        chunks = []
        for doc, meta in zip(results.get("documents", []), results.get("metadatas", [])):
            if meta and meta.get("source") == doc_name:
                chunks.append((meta.get("chunk_index", 0), doc))
        chunks.sort(key=lambda x: x[0])
        content = "\n\n".join(c for _, c in chunks)
        return {"content": content, "total_chunks": len(chunks)}
    except Exception as e:
        return {"error": str(e)}


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NGO Proposal Drafting Bot",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #4a4a4a !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stRadio > label { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stRadio > div { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stToggle > label { color: #FFFFFF !important; }
    [data-testid="stSidebar"] p { color: #FFFFFF !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    .stButton > button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton > button:hover { background-color: #CC0000 !important; color: #FFFFFF !important; }
    .stButton > button:active { background-color: #990000 !important; color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">📋 NGO Bot</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Proposal Drafting Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 0.5rem;'>📊 Knowledge Base</p>", unsafe_allow_html=True)
    stats = get_kb_stats_direct()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Documents</p>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">{stats.get("total_documents", 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Chunks</p>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">{stats.get("total_chunks", 0)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 0.5rem;'>🧭 Navigation</p>", unsafe_allow_html=True)
    page = st.radio(
        "Go to",
        ["💬 Chat / Q&A", "✍️ Draft Proposal", "📁 Upload Documents", "📋 Knowledge Base", "🔧 Admin Panel"],
        label_visibility="collapsed",
    )

    st.divider()
    if "use_memory" not in st.session_state:
        st.session_state.use_memory = True
    st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 0.5rem;'>⚙️ Settings</p>", unsafe_allow_html=True)
    st.session_state.use_memory = st.toggle(
        "🧠 Conversation Memory",
        value=st.session_state.use_memory,
        help="Remember previous messages in this session",
    )

    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: rgba(255,255,255,0.7); font-size: 0.8rem;">
        <p style="margin: 0.25rem 0;">Week 3 Deliverable</p>
        <p style="margin: 0.25rem 0;">LangChain • ChromaDB • Streamlit</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.5);">PRJ-032 | Yeshwanth Sai R</p>
    </div>
    """, unsafe_allow_html=True)


# ── Session ID ────────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session"


# ── Page: Chat / Q&A ──────────────────────────────────────────────────────────
if page == "💬 Chat / Q&A":
    st.title("💬 Chat with NGO Knowledge Base")
    st.caption("Ask questions about NGO proposals, grant writing, and program design.")

    if st.session_state.use_memory:
        st.info("🧠 **Conversation Memory ON** — I remember your previous questions in this session.")
    else:
        st.warning("🧠 **Conversation Memory OFF** — Each question is answered independently.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "timestamp": get_current_timestamp(),
            "content": (
                "Hello! I'm your NGO Proposal Drafting Assistant. 👋\n\n"
                "I can help you with:\n"
                "- **Grant proposal structure** and best practices\n"
                "- **Program design** and logical frameworks\n"
                "- **Budget planning** for NGO projects\n"
                "- **Donor requirements** and reporting standards\n\n"
                "💡 **New in Week 3:** Use the **✍️ Draft Proposal** tab to generate a complete NGO proposal!\n\n"
                "Upload documents in the **Upload Documents** tab to get answers grounded in your specific NGO materials!"
            ),
        }]

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("timestamp"):
                st.caption(f"🕐 {format_timestamp_for_display(msg['timestamp'])}")
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                real_sources = [s for s in msg.get("sources", []) if "General Knowledge" not in s]
                if real_sources:
                    with st.expander("📎 Sources"):
                        for src in real_sources:
                            st.write(f"📄 {src}")
                if msg.get("citations"):
                    with st.expander("🔖 Citations"):
                        for cite in msg["citations"]:
                            st.caption(cite)

    if prompt := st.chat_input("Ask about NGO proposals, grant writing, or your uploaded documents..."):
        st.session_state.messages.append({
            "role": "user", "content": prompt, "timestamp": get_current_timestamp(),
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = ask_question_direct(prompt, st.session_state.session_id, st.session_state.use_memory)

            answer = result.get("answer", "Sorry, I could not generate an answer.")
            sources = result.get("sources", [])
            citations = result.get("citations", [])
            chunks_used = result.get("chunks_used", 0)

            st.markdown(answer)
            real_sources = [s for s in sources if "General Knowledge" not in s]
            if real_sources:
                with st.expander("📎 Sources"):
                    for src in real_sources:
                        st.write(f"📄 {src}")
            if citations:
                with st.expander("🔖 Citations"):
                    for cite in citations:
                        st.caption(cite)
            if chunks_used > 0:
                st.caption(f"📊 Used {chunks_used} relevant chunk(s) from knowledge base")

            st.session_state.messages.append({
                "role": "assistant",
                "timestamp": result.get("timestamp", get_current_timestamp()),
                "content": answer,
                "sources": real_sources,
                "citations": citations,
            })

    col1, col2 = st.columns(2)
    with col1:
        if len(st.session_state.get("messages", [])) > 1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
    with col2:
        if len(st.session_state.get("messages", [])) > 1:
            if st.button("🧠 Clear Memory"):
                clear_conversation(st.session_state.session_id)
                st.success("Memory cleared!")


# ── Page: Draft Proposal ──────────────────────────────────────────────────────
elif page == "✍️ Draft Proposal":
    st.title("✍️ NGO Proposal Draft Generator")
    st.caption("Fill in your project details and generate a professional grant proposal.")
    st.info("💡 Enter your project details below, choose a section, then download the result.")

    section_options = {
        "full_proposal": "📄 Complete Proposal (All Sections)",
        "executive_summary": "📝 Executive Summary",
        "problem_statement": "🔍 Problem Statement",
        "objectives": "🎯 Project Objectives",
        "methodology": "⚙️ Methodology / Implementation Plan",
        "budget": "💰 Budget Breakdown",
        "monitoring_evaluation": "📊 Monitoring & Evaluation Plan",
    }

    with st.form("proposal_form"):
        st.subheader("📋 Project Details")
        col1, col2 = st.columns(2)
        with col1:
            org_name = st.text_input("Organization Name *", placeholder="e.g., Hope Foundation")
            project_title = st.text_input("Project Title *", placeholder="e.g., Rural Education Development Program")
            location = st.text_input("Project Location", placeholder="e.g., Rural Tamil Nadu")
            duration = st.selectbox("Project Duration", ["6 months", "12 months", "18 months", "24 months", "36 months"], index=1)
        with col2:
            beneficiaries = st.text_input("Target Beneficiaries *", placeholder="e.g., 500 children aged 6-16")
            budget = st.text_input("Total Budget", placeholder="e.g., ₹600,000 or $10,000")
            activities = st.text_area("Key Activities", placeholder="e.g., Digital classrooms, teacher training", height=80)

        problem = st.text_area("Problem Statement *", placeholder="Describe the problem your project addresses.", height=120)
        selected_section = st.selectbox("Choose section", options=list(section_options.keys()), format_func=lambda x: section_options[x])
        submitted = st.form_submit_button("🚀 Generate Proposal", type="primary", use_container_width=True)

    if submitted:
        if not org_name or not project_title or not problem or not beneficiaries:
            st.error("❌ Please fill in: Organization Name, Project Title, Problem, and Beneficiaries.")
        else:
            with st.spinner(f"✍️ Generating {section_options[selected_section]}... This may take 30-60 seconds."):
                result = generate_proposal_direct({
                    "org_name": org_name, "project_title": project_title,
                    "problem": problem, "beneficiaries": beneficiaries,
                    "location": location, "duration": duration,
                    "budget": budget, "activities": activities,
                }, selected_section)

            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success(f"✅ {section_options[selected_section]} generated successfully!")
                st.session_state["generated_proposal"] = result
                st.session_state["proposal_section"] = selected_section
                st.session_state["proposal_title"] = project_title

    if st.session_state.get("generated_proposal"):
        result = st.session_state["generated_proposal"]
        section = st.session_state.get("proposal_section", "proposal")
        title = st.session_state.get("proposal_title", "proposal")
        st.divider()
        st.subheader(f"📄 Generated: {section_options.get(section, section)}")
        st.caption(f"Generated at: {result.get('generated_at', '')}")
        content = result.get("content", "")
        st.markdown(content)
        st.divider()
        st.subheader("📥 Export Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📄 Download as TXT", data=content,
                               file_name=f"{title.replace(' ', '_')}_{section}.txt", mime="text/plain", use_container_width=True)
        with col2:
            st.download_button("📝 Download as Markdown", data=f"# {title}\n\n{content}",
                               file_name=f"{title.replace(' ', '_')}_{section}.md", mime="text/markdown", use_container_width=True)
        with col3:
            if st.button("🗑️ Clear Draft", use_container_width=True):
                st.session_state.pop("generated_proposal", None)
                st.rerun()

    st.divider()
    st.subheader("✅ Proposal Submission Checklist")
    col1, col2 = st.columns(2)
    with col1:
        checklist_org = st.text_input("Organization Name", key="checklist_org", placeholder="Your NGO name")
    with col2:
        checklist_title = st.text_input("Project Title", key="checklist_title", placeholder="Your project title")
    if st.button("📋 Generate Checklist"):
        checklist_content = generate_checklist({"org_name": checklist_org or "Your Organization", "project_title": checklist_title or "Your Project"})
        st.markdown(checklist_content)
        st.download_button("📥 Download Checklist", data=checklist_content, file_name="proposal_checklist.md", mime="text/markdown")


# ── Page: Upload Documents ────────────────────────────────────────────────────
elif page == "📁 Upload Documents":
    st.title("📁 Upload Documents to Knowledge Base")
    st.caption("Upload NGO documents, grant templates, or reference materials.")
    st.info("**Supported formats:** PDF, TXT, DOCX  \n**Max file size:** 10MB")

    uploaded_files = st.file_uploader("Choose files to upload", type=["pdf", "txt", "docx", "doc"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("📤 Upload to Knowledge Base", type="primary"):
            progress = st.progress(0)
            results = []
            for i, f in enumerate(uploaded_files):
                with st.spinner(f"Processing {f.name}..."):
                    result = upload_document_direct(f.name, f.getvalue())
                    if "error" not in result:
                        results.append(result)
                    else:
                        st.error(f"❌ {f.name}: {result['error']}")
                progress.progress((i + 1) / len(uploaded_files))
            progress.empty()
            if results:
                st.success(f"✅ Processed {len(results)} file(s) successfully!")
                for r in results:
                    st.write(f"• **{r['filename']}** → {r['chunks_created']} chunks created")
                st.cache_resource.clear()
                st.rerun()

    st.divider()
    st.subheader("📄 Load Sample Documents")
    if st.button("📥 Load Sample NGO Documents"):
        sample_dir = Path("./data/sample_docs")
        sample_files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))
        if not sample_files:
            st.warning("No sample documents found in ./data/sample_docs/")
        else:
            loaded = 0
            for sample_file in sample_files:
                result = upload_document_direct(sample_file.name, sample_file.read_bytes())
                if "error" not in result:
                    loaded += 1
            if loaded:
                st.success(f"✅ Loaded {loaded} sample document(s)!")
                st.cache_resource.clear()
                st.rerun()


# ── Page: Knowledge Base ──────────────────────────────────────────────────────
elif page == "📋 Knowledge Base":
    st.title("📋 Knowledge Base Status")

    stats = get_kb_stats_direct()
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Documents", stats.get("total_documents", 0))
    col2.metric("🧩 Chunks", stats.get("total_chunks", 0))
    col3.metric("🗄️ Collection", stats.get("collection_name", "N/A"))

    st.divider()
    st.subheader("Indexed Documents")
    documents = stats.get("documents", [])

    if documents:
        for doc in documents:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📄 {doc}", key=f"preview_{doc}"):
                    st.session_state["preview_doc"] = doc
            with col2:
                if st.button("🗑️", key=f"delete_{doc}", help=f"Delete {doc}"):
                    with st.spinner(f"Deleting {doc}..."):
                        result = delete_document_direct(doc)
                    if "error" not in result:
                        if st.session_state.get("preview_doc") == doc:
                            st.session_state.pop("preview_doc", None)
                        st.success(f"Deleted '{doc}'")
                        st.cache_resource.clear()
                        st.rerun()
                    else:
                        st.error(result["error"])

        if st.session_state.get("preview_doc"):
            preview_doc = st.session_state["preview_doc"]
            st.divider()
            c1, c2 = st.columns([5, 1])
            with c1:
                st.subheader(f"📖 {preview_doc}")
            with c2:
                if st.button("✖ Close"):
                    st.session_state.pop("preview_doc", None)
                    st.rerun()
            with st.spinner("Loading document..."):
                preview_data = get_document_preview_direct(preview_doc)
            if "error" not in preview_data:
                st.metric("Chunks", preview_data.get("total_chunks", 0))
                st.markdown(
                    f"""<div style="background-color:#1e1e1e;border:1px solid #444;border-radius:8px;
                    padding:20px;height:400px;overflow-y:auto;font-family:monospace;font-size:14px;
                    color:#ffffff;white-space:pre-wrap;line-height:1.6;">
                    {preview_data.get("content","").replace("<","&lt;").replace(">","&gt;")}
                    </div>""", unsafe_allow_html=True)
                st.download_button("⬇️ Download", data=preview_data.get("content", ""),
                                   file_name=preview_doc, mime="text/plain")
    else:
        st.info("No documents in the knowledge base yet. Go to **Upload Documents** to add some.")

    st.divider()
    with st.expander("⚠️ Danger Zone"):
        st.warning("Clearing the knowledge base will remove all indexed documents. This cannot be undone.")
        if st.button("🗑️ Clear Knowledge Base"):
            result = clear_kb_direct()
            st.success("Knowledge base cleared.")
            st.rerun()


# ── Page: Admin Panel ─────────────────────────────────────────────────────────
elif page == "🔧 Admin Panel":
    st.title("🔧 Admin Panel")
    st.caption("Access control, session management, chat history, and system tools.")

    st.subheader("🔐 Admin Access")
    if not st.session_state.get("admin_logged_in", False):

        # ── Login Form ────────────────────────────────────────────────────────
        with st.form("admin_login_form"):
            password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button("🔑 Login as Admin", type="primary", use_container_width=True)
            with col2:
                request_btn = st.form_submit_button("📩 Request Admin Access", use_container_width=True)

        if login_btn:
            if verify_admin(password):
                st.session_state["admin_logged_in"] = True
                st.success("✅ Admin login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password. Try again.")

        if request_btn:
            st.session_state["show_request_form"] = True

        # ── Request Admin Access Form ─────────────────────────────────────────
        if st.session_state.get("show_request_form", False):
            st.divider()
            st.subheader("📩 Request Admin Access")
            st.caption("Fill in your details and your request will be sent to the administrator.")

            with st.form("request_access_form"):
                req_name  = st.text_input("Your Full Name *", placeholder="e.g., John Doe")
                req_email = st.text_input("Your Email *", placeholder="e.g., john@example.com")
                req_org   = st.text_input("Organization", placeholder="e.g., Hope Foundation")
                req_reason = st.text_area("Reason for Access *",
                                          placeholder="Why do you need admin access?",
                                          height=100)
                send_btn = st.form_submit_button("📤 Send Request", type="primary", use_container_width=True)
                cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)

            if cancel_btn:
                st.session_state["show_request_form"] = False
                st.rerun()

            if send_btn:
                if not req_name or not req_email or not req_reason:
                    st.error("❌ Please fill in: Name, Email, and Reason.")
                else:
                    # Send email via SMTP (Gmail)
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart

                    ADMIN_EMAIL   = "yeshwanthsair@gmail.com"
                    SENDER_EMAIL  = os.getenv("SENDER_EMAIL", "")
                    SENDER_PASS   = os.getenv("SENDER_PASSWORD", "")

                    subject = f"[NGO Bot] Admin Access Request from {req_name}"
                    body = f"""
New Admin Access Request - NGO Proposal Drafting Bot
=====================================================

Name        : {req_name}
Email       : {req_email}
Organization: {req_org or 'Not provided'}
Timestamp   : {get_current_timestamp()}

Reason for Access:
{req_reason}

=====================================================
To approve: Share the admin password with this user.
To deny   : No action needed.
                    """.strip()

                    try:
                        if SENDER_EMAIL and SENDER_PASS:
                            msg = MIMEMultipart()
                            msg["From"]    = SENDER_EMAIL
                            msg["To"]      = ADMIN_EMAIL
                            msg["Subject"] = subject
                            msg.attach(MIMEText(body, "plain"))

                            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                server.login(SENDER_EMAIL, SENDER_PASS)
                                server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())

                            st.success(f"✅ Request sent to {ADMIN_EMAIL}! The admin will contact you at {req_email}.")
                        else:
                            # Fallback: show the request info so admin can note it manually
                            st.warning("⚠️ Email not configured. Showing request details below.")
                            st.info(f"""
**Request Submitted:**
- **Name:** {req_name}
- **Email:** {req_email}
- **Organization:** {req_org or 'N/A'}
- **Reason:** {req_reason}

📧 Please contact **{ADMIN_EMAIL}** directly with this information.
                            """)

                        st.session_state["show_request_form"] = False
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")
                        st.info(f"Please contact the admin directly at **{ADMIN_EMAIL}** with your request.")

        st.info("💡 Default admin password is set in .env file: ADMIN_PASSWORD=yourpassword")
        st.stop()

    st.success("✅ Logged in as Admin")
    if st.button("🚪 Logout"):
        st.session_state["admin_logged_in"] = False
        st.rerun()

    st.divider()

    # Session stats
    st.subheader("👥 Session Management")
    sess_stats = get_session_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", sess_stats.get("total_sessions", 0))
    col2.metric("Admin Sessions", sess_stats.get("admin_sessions", 0))
    col3.metric("User Sessions", sess_stats.get("user_sessions", 0))
    col4.metric("Total Messages", sess_stats.get("total_messages", 0))

    all_sessions = get_all_sessions()
    if all_sessions:
        with st.expander(f"📋 View All Sessions ({len(all_sessions)})"):
            for s in all_sessions:
                role_icon = "👑" if s.get("role") == "admin" else "👤"
                st.write(f"{role_icon} **{s['session_id'][:16]}...** | Role: {s['role']} | "
                         f"Messages: {s['message_count']} | Last active: {format_timestamp_for_display(s['last_active'])}")

    st.divider()

    # Chat history
    st.subheader("📜 Chat History Logs")
    log_stats = get_log_stats()
    col1, col2 = st.columns(2)
    col1.metric("Total Interactions", log_stats.get("total_interactions", 0))
    col2.metric("Total Sessions", log_stats.get("total_sessions", 0))

    all_entries = get_chat_history(limit=500)
    available_sessions = sorted(list({e.get("session_id", "unknown") for e in all_entries}))
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("🔍 Search questions/answers:", placeholder="e.g. budget, proposal...")
    with col2:
        selected_session = st.selectbox("📋 Filter by Session:", ["All Sessions"] + available_sessions)
    limit_n = st.slider("Show last N interactions", 5, 100, 20)

    filtered = all_entries[:limit_n]
    if selected_session != "All Sessions":
        filtered = [e for e in filtered if e.get("session_id") == selected_session]
    if search_query.strip():
        sl = search_query.strip().lower()
        filtered = [e for e in filtered if sl in e["question"].lower() or sl in e["answer"].lower()]

    st.info(f"📊 Showing **{len(filtered)}** interaction(s)")

    if filtered:
        export_lines = []
        for entry in filtered:
            export_lines += [f"Timestamp: {entry['timestamp']}", f"Session: {entry.get('session_id','')}",
                             f"Question: {entry['question']}", f"Answer: {entry['answer']}", "-"*80]
        st.download_button("📥 Export Chat History", data="\n".join(export_lines),
                           file_name=f"chat_history_{len(filtered)}_entries.txt", mime="text/plain")

        for idx, entry in enumerate(filtered):
            q_preview = entry["question"][:55] + "..." if len(entry["question"]) > 55 else entry["question"]
            with st.expander(f"🕐 {format_timestamp_for_display(entry['timestamp'])} | {q_preview}"):
                st.write(f"**❓ Question:** {entry['question']}")
                st.divider()
                st.write("**💬 Answer:**")
                st.markdown(entry["answer"])
                if entry.get("sources"):
                    st.write(f"**📎 Sources:** {', '.join(entry['sources'])}")
    else:
        st.info("💬 No chat history yet. Start chatting in the **Chat / Q&A** tab!")

    st.divider()
    with st.expander("⚠️ Danger Zone"):
        st.warning("These actions are irreversible.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat History Logs"):
                clear_history()
                st.success("Chat history cleared.")
        with col2:
            if st.button("🗑️ Clear Knowledge Base"):
                clear_kb_direct()
                st.success("Knowledge base cleared.")
                st.rerun()
