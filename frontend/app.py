"""
NGO Proposal Drafting Bot - Streamlit Frontend
Week 3: Proposal generator, conversation memory, access control, export

Run with: streamlit run frontend/app.py
"""
import streamlit as st
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def get_current_timestamp() -> str:
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def format_timestamp_for_display(timestamp_str: str) -> str:
    if " at " in timestamp_str:
        return timestamp_str
    try:
        if 'T' in timestamp_str:
            clean = timestamp_str.split('+')[0].split('Z')[0]
            dt = datetime.fromisoformat(clean)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        return timestamp_str
    except (ValueError, AttributeError):
        return timestamp_str[:19] if len(timestamp_str) > 19 else timestamp_str


st.set_page_config(
    page_title="NGO Proposal Drafting Bot",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Styling ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #4a4a4a !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stToggle > label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton > button:hover {
        background-color: #CC0000 !important;
        color: #FFFFFF !important;
    }
    
    .stButton > button:active {
        background-color: #990000 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Helper functions ─────────────────────────────────────────────────────────

def api_delete(endpoint: str) -> dict | None:
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
    try:
        if files:
            resp = requests.post(f"{API_BASE}{endpoint}", files=files, timeout=120)
        else:
            resp = requests.post(f"{API_BASE}{endpoint}", json=json_data, timeout=120)
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
    result = api_get("/documents/stats")
    return result or {"total_documents": 0, "total_chunks": 0, "collection_name": "N/A"}


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">📋 NGO Bot</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Proposal Drafting Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # Knowledge Base Stats
    st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 0.5rem;'>📊 Knowledge Base</p>", unsafe_allow_html=True)
    stats = get_kb_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Documents</p>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">
                {stats.get("total_documents", 0)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Chunks</p>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">
                {stats.get("total_chunks", 0)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 0.5rem;'>🧭 Navigation</p>", unsafe_allow_html=True)
    page = st.radio(
        "Go to",
        [
            "💬 Chat / Q&A",
            "✍️ Draft Proposal",
            "📁 Upload Documents",
            "📋 Knowledge Base",
            "🔧 Admin Panel",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Memory toggle
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
        <p style="margin: 0.25rem 0;">FastAPI • LangChain • ChromaDB</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.5);">
            PRJ-032 | Yeshwanth Sai R
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Page: Chat / Q&A ─────────────────────────────────────────────────────────

if page == "💬 Chat / Q&A":
    st.title("💬 Chat with NGO Knowledge Base")
    st.caption("Ask questions about NGO proposals, grant writing, and program design.")

    # Memory status indicator
    if st.session_state.use_memory:
        st.info("🧠 **Conversation Memory ON** — I remember your previous questions in this session.")
    else:
        st.warning("🧠 **Conversation Memory OFF** — Each question is answered independently.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
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
                "Upload documents in the **Upload Documents** tab to get answers "
                "grounded in your specific NGO materials!"
            ),
        })

    # Display chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("timestamp"):
                st.caption(f"🕐 {format_timestamp_for_display(msg['timestamp'])}")
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                col1, col2, col3 = st.columns([1, 1, 10])
                with col1:
                    if st.button("📋", key=f"copy_{idx}", help="Copy to clipboard"):
                        st.code(msg["content"], language=None)
                with col2:
                    if st.button("🔄", key=f"regen_{idx}", help="Regenerate response"):
                        if idx > 0 and st.session_state.messages[idx - 1]["role"] == "user":
                            user_question = st.session_state.messages[idx - 1]["content"]
                            st.session_state.messages.pop(idx)
                            with st.spinner("Regenerating..."):
                                result = api_post("/chat/ask", json_data={
                                    "question": user_question,
                                    "session_id": "streamlit_session",
                                    "use_memory": st.session_state.use_memory,
                                })
                            if result:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "timestamp": result.get("timestamp", get_current_timestamp()),
                                    "content": result.get("answer", ""),
                                    "sources": [s for s in result.get("sources", []) if "General Knowledge" not in s],
                                    "citations": result.get("citations", []),
                                })
                            st.rerun()

                real_sources = [s for s in msg.get("sources", []) if "General Knowledge" not in s]
                if real_sources:
                    with st.expander("📎 Sources"):
                        for src in real_sources:
                            if st.button(f"📄 {src}", key=f"view_src_{idx}_{src}"):
                                st.session_state["preview_doc"] = src
                                st.session_state["show_doc_modal"] = True
                                st.rerun()

                citations = msg.get("citations", [])
                if citations:
                    with st.expander("🔖 Citations"):
                        for cite in citations:
                            st.caption(cite)

            elif msg["role"] == "user":
                if st.button("✏️", key=f"edit_{idx}", help="Edit message"):
                    st.session_state[f"editing_{idx}"] = True
                    st.rerun()

                if st.session_state.get(f"editing_{idx}", False):
                    edited_text = st.text_area(
                        "Edit your message:",
                        value=msg["content"],
                        key=f"edit_input_{idx}",
                        height=100,
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save", key=f"save_{idx}"):
                            st.session_state.messages[idx]["content"] = edited_text
                            st.session_state[f"editing_{idx}"] = False
                            st.session_state.messages = st.session_state.messages[:idx + 1]
                            with st.spinner("Generating new response..."):
                                result = api_post("/chat/ask", json_data={
                                    "question": edited_text,
                                    "session_id": "streamlit_session",
                                    "use_memory": st.session_state.use_memory,
                                })
                            if result:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "timestamp": result.get("timestamp", get_current_timestamp()),
                                    "content": result.get("answer", ""),
                                    "sources": [s for s in result.get("sources", []) if "General Knowledge" not in s],
                                    "citations": result.get("citations", []),
                                })
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()

    # Document preview modal
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
                f"""<div style="background-color:#1e1e1e;border:1px solid #444;border-radius:8px;
                padding:20px;height:400px;overflow-y:auto;font-family:monospace;font-size:14px;
                color:#ffffff;white-space:pre-wrap;line-height:1.6;">
                {preview_data.get("content","").replace("<","&lt;").replace(">","&gt;")}
                </div>""",
                unsafe_allow_html=True,
            )
            st.download_button("⬇️ Download", data=preview_data.get("content", ""),
                               file_name=preview_doc, mime="text/plain")

    # Chat input
    if prompt := st.chat_input("Ask about NGO proposals, grant writing, or your uploaded documents..."):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": get_current_timestamp(),
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post("/chat/ask", json_data={
                    "question": prompt,
                    "session_id": "streamlit_session",
                    "use_memory": st.session_state.use_memory,
                })

            if result:
                answer = result.get("answer", "Sorry, I could not generate an answer.")
                sources = result.get("sources", [])
                citations = result.get("citations", [])
                chunks_used = result.get("chunks_used", 0)

                st.markdown(answer)

                real_sources = [s for s in sources if "General Knowledge" not in s]
                if real_sources:
                    with st.expander("📎 Sources"):
                        for src in real_sources:
                            if st.button(f"📄 {src}", key=f"view_src_new_{src}"):
                                st.session_state["preview_doc"] = src
                                st.session_state["show_doc_modal"] = True
                                st.rerun()

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
        if st.session_state.messages and len(st.session_state.messages) > 1:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.messages = []
                st.rerun()
    with col2:
        if st.session_state.messages and len(st.session_state.messages) > 1:
            if st.button("🧠 Clear Memory", type="secondary", help="Clear server-side conversation memory"):
                api_post("/chat/session/clear", json_data={"session_id": "streamlit_session"})
                st.success("Memory cleared!")


# ── Page: Draft Proposal (Week 3) ────────────────────────────────────────────

elif page == "✍️ Draft Proposal":
    st.title("✍️ NGO Proposal Draft Generator")
    st.caption("Fill in your project details and generate a professional grant proposal.")

    st.info(
        "💡 **How it works:** Enter your project details below, choose a section to generate, "
        "then download the result. You can generate individual sections or the full proposal."
    )

    with st.form("proposal_form"):
        st.subheader("📋 Project Details")

        col1, col2 = st.columns(2)
        with col1:
            org_name = st.text_input(
                "Organization Name *",
                placeholder="e.g., Hope Foundation",
                help="Your NGO's official name",
            )
            project_title = st.text_input(
                "Project Title *",
                placeholder="e.g., Rural Education Development Program",
            )
            location = st.text_input(
                "Project Location",
                placeholder="e.g., Rural Tamil Nadu, South India",
            )
            duration = st.selectbox(
                "Project Duration",
                ["6 months", "12 months", "18 months", "24 months", "36 months"],
                index=1,
            )

        with col2:
            beneficiaries = st.text_input(
                "Target Beneficiaries *",
                placeholder="e.g., 500 children aged 6-16 in 10 villages",
            )
            budget = st.text_input(
                "Total Budget",
                placeholder="e.g., ₹600,000 or $10,000",
            )
            activities = st.text_area(
                "Key Activities",
                placeholder="e.g., Digital classrooms, teacher training, school supplies",
                height=80,
            )

        problem = st.text_area(
            "Problem Statement *",
            placeholder="Describe the problem your project addresses. Include data/statistics if available.",
            height=120,
        )

        st.subheader("📄 Select Section to Generate")
        section_options = {
            "full_proposal": "📄 Complete Proposal (All Sections)",
            "executive_summary": "📝 Executive Summary",
            "problem_statement": "🔍 Problem Statement",
            "objectives": "🎯 Project Objectives",
            "methodology": "⚙️ Methodology / Implementation Plan",
            "budget": "💰 Budget Breakdown",
            "monitoring_evaluation": "📊 Monitoring & Evaluation Plan",
        }
        selected_section = st.selectbox(
            "Choose section",
            options=list(section_options.keys()),
            format_func=lambda x: section_options[x],
        )

        submitted = st.form_submit_button("🚀 Generate Proposal", type="primary", use_container_width=True)

    if submitted:
        if not org_name or not project_title or not problem or not beneficiaries:
            st.error("❌ Please fill in the required fields: Organization Name, Project Title, Problem, and Beneficiaries.")
        else:
            with st.spinner(f"✍️ Generating {section_options[selected_section]}... This may take 30-60 seconds."):
                result = api_post("/proposals/generate", json_data={
                    "org_name": org_name,
                    "project_title": project_title,
                    "problem": problem,
                    "beneficiaries": beneficiaries,
                    "location": location,
                    "duration": duration,
                    "budget": budget,
                    "activities": activities,
                    "section": selected_section,
                })

            if result:
                st.success(f"✅ {section_options[selected_section]} generated successfully!")
                st.session_state["generated_proposal"] = result
                st.session_state["proposal_section"] = selected_section
                st.session_state["proposal_title"] = project_title

    # Display generated proposal
    if st.session_state.get("generated_proposal"):
        result = st.session_state["generated_proposal"]
        section = st.session_state.get("proposal_section", "proposal")
        title = st.session_state.get("proposal_title", "proposal")

        st.divider()
        st.subheader(f"📄 Generated: {section_options.get(section, section)}")
        st.caption(f"Generated at: {result.get('generated_at', '')}")

        # Display the content
        content = result.get("content", "")
        st.markdown(content)

        st.divider()

        # Export options
        st.subheader("📥 Export Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            filename = f"{title.replace(' ', '_')}_{section}.txt"
            st.download_button(
                "📄 Download as TXT",
                data=content,
                file_name=filename,
                mime="text/plain",
                use_container_width=True,
            )

        with col2:
            # Markdown format
            md_content = f"# {title}\n\n{content}"
            st.download_button(
                "📝 Download as Markdown",
                data=md_content,
                file_name=f"{title.replace(' ', '_')}_{section}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col3:
            if st.button("🗑️ Clear Draft", use_container_width=True):
                st.session_state.pop("generated_proposal", None)
                st.rerun()

    st.divider()

    # Checklist generator
    st.subheader("✅ Proposal Submission Checklist")
    st.caption("Generate a checklist of everything you need to submit with your proposal.")

    col1, col2 = st.columns(2)
    with col1:
        checklist_org = st.text_input("Organization Name", key="checklist_org", placeholder="Your NGO name")
    with col2:
        checklist_title = st.text_input("Project Title", key="checklist_title", placeholder="Your project title")

    if st.button("📋 Generate Checklist", type="secondary"):
        with st.spinner("Generating checklist..."):
            result = api_post("/proposals/checklist", json_data={
                "org_name": checklist_org or "Your Organization",
                "project_title": checklist_title or "Your Project",
                "problem": "",
                "beneficiaries": "",
            })
        if result:
            checklist_content = result.get("checklist", "")
            st.markdown(checklist_content)
            st.download_button(
                "📥 Download Checklist",
                data=checklist_content,
                file_name="proposal_checklist.md",
                mime="text/markdown",
            )


# ── Page: Upload Documents ────────────────────────────────────────────────────

elif page == "📁 Upload Documents":
    st.title("📁 Upload Documents to Knowledge Base")
    st.caption("Upload NGO documents, grant templates, or reference materials.")

    st.info(
        "**Supported formats:** PDF, TXT, DOCX  \n"
        "**Max file size:** 10MB  \n"
        "Documents are parsed, chunked, and stored in ChromaDB for semantic search."
    )

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "txt", "docx", "doc"],
        accept_multiple_files=True,
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
            if results:
                st.success(f"✅ Processed {len(results)} file(s) successfully!")
                for r in results:
                    st.write(f"• **{r['filename']}** → {r['chunks_created']} chunks created")
                st.rerun()

    st.divider()
    st.subheader("📄 Load Sample Documents")
    st.caption("Load pre-built NGO sample documents to test the system.")

    if st.button("📥 Load Sample NGO Documents", type="secondary"):
        sample_dir = Path("./data/sample_docs")
        sample_files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))
        if not sample_files:
            st.warning("No sample documents found.")
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


# ── Page: Knowledge Base ──────────────────────────────────────────────────────

elif page == "📋 Knowledge Base":
    st.title("📋 Knowledge Base Status")

    stats = get_kb_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Documents", stats.get("total_documents", 0))
    col2.metric("🧩 Chunks", stats.get("total_chunks", 0))
    col3.metric("🗄️ Collection", stats.get("collection_name", "N/A"))

    st.divider()
    st.subheader("Indexed Documents")
    doc_list = api_get("/documents/list")

    if doc_list and doc_list.get("documents"):
        for doc in doc_list["documents"]:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📄 {doc}", key=f"preview_{doc}", help="Click to preview"):
                    st.session_state["preview_doc"] = doc
            with col2:
                if st.button("🗑️", key=f"delete_{doc}", help=f"Delete {doc}"):
                    with st.spinner(f"Deleting {doc}..."):
                        result = api_delete(f"/documents/delete/{doc}")
                        if result:
                            if st.session_state.get("preview_doc") == doc:
                                st.session_state.pop("preview_doc", None)
                            st.success(f"Deleted '{doc}'")
                            st.rerun()

        if st.session_state.get("preview_doc"):
            preview_doc = st.session_state["preview_doc"]
            st.divider()
            col1, col2 = st.columns([5, 1])
            with col1:
                st.subheader(f"📖 {preview_doc}")
            with col2:
                if st.button("✖ Close", key="close_preview"):
                    st.session_state.pop("preview_doc", None)
                    st.rerun()
            with st.spinner("Loading document..."):
                preview_data = api_get(f"/documents/preview/{preview_doc}")
            if preview_data:
                c1, c2 = st.columns(2)
                c1.metric("Chunks", preview_data.get("total_chunks", 0))
                c2.metric("Characters", len(preview_data.get("content", "")))
                st.markdown(
                    f"""<div style="background-color:#1e1e1e;border:1px solid #444;border-radius:8px;
                    padding:20px;height:400px;overflow-y:auto;font-family:monospace;font-size:14px;
                    color:#ffffff;white-space:pre-wrap;line-height:1.6;">
                    {preview_data.get("content","").replace("<","&lt;").replace(">","&gt;")}
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.download_button(
                    "⬇️ Download Content",
                    data=preview_data.get("content", ""),
                    file_name=preview_doc,
                    mime="text/plain",
                )
    else:
        st.info("No documents in the knowledge base yet. Go to **Upload Documents** to add some.")

    st.divider()
    with st.expander("⚠️ Danger Zone"):
        st.warning("Clearing the knowledge base will remove all indexed documents. This cannot be undone.")
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            result = api_post("/documents/clear")
            if result:
                st.success("Knowledge base cleared.")
                st.rerun()


# ── Page: Admin Panel (Week 3) ────────────────────────────────────────────────

elif page == "🔧 Admin Panel":
    st.title("🔧 Admin Panel")
    st.caption("Week 3: Access control, session management, chat history, and system tools.")

    # ── Week 3: Admin Login ──────────────────────────────────────────────────
    st.subheader("🔐 Admin Access")

    if not st.session_state.get("admin_logged_in", False):
        with st.form("admin_login_form"):
            password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
            login_btn = st.form_submit_button("🔑 Login as Admin", type="primary")

        if login_btn:
            result = api_post("/chat/admin/login", json_data={"password": password})
            if result and result.get("success"):
                st.session_state["admin_logged_in"] = True
                st.session_state["admin_session_id"] = result.get("session_id")
                st.success("✅ Admin login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password. Try again.")

        st.info("💡 Default admin password: **Yeshwanth@2006** (change in .env file: ADMIN_PASSWORD=yourpassword)")
        st.stop()

    # ── Admin is logged in ───────────────────────────────────────────────────
    st.success("✅ Logged in as Admin")
    
    if st.button("🚪 Logout", type="secondary"):
        st.session_state["admin_logged_in"] = False
        st.session_state.pop("admin_session_id", None)
        st.rerun()

    st.divider()

    # ── Session Management ───────────────────────────────────────────────────
    st.subheader("👥 Session Management")
    sessions_data = api_get("/chat/sessions")
    if sessions_data:
        stats_s = sessions_data.get("stats", {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sessions", stats_s.get("total_sessions", 0))
        col2.metric("Admin Sessions", stats_s.get("admin_sessions", 0))
        col3.metric("User Sessions", stats_s.get("user_sessions", 0))
        col4.metric("Total Messages", stats_s.get("total_messages", 0))

        sessions = sessions_data.get("sessions", [])
        if sessions:
            with st.expander(f"📋 View All Sessions ({len(sessions)})"):
                for s in sessions:
                    role_icon = "👑" if s.get("role") == "admin" else "👤"
                    st.write(
                        f"{role_icon} **{s['session_id'][:16]}...** | "
                        f"Role: {s['role']} | "
                        f"Messages: {s['message_count']} | "
                        f"Last active: {format_timestamp_for_display(s['last_active'])}"
                    )

    st.divider()

    # ── KB Refresh ───────────────────────────────────────────────────────────
    st.subheader("🔄 Knowledge Base Refresh")
    if st.button("🔄 Refresh Knowledge Base", type="primary"):
        with st.spinner("Refreshing..."):
            result = api_post("/chat/admin/refresh")
        if result:
            st.success("✅ Knowledge base refreshed!")
            st.json(result.get("stats", {}))

    st.divider()

    # ── Chat History ─────────────────────────────────────────────────────────
    st.subheader("📜 Chat History Logs")
    history_stats = api_get("/chat/history/stats")
    if history_stats:
        col1, col2 = st.columns(2)
        col1.metric("Total Interactions", history_stats.get("total_interactions", 0))
        col2.metric("Total Sessions", history_stats.get("total_sessions", 0))

    # Auto-load all history to get available session IDs
    all_history_data = api_get("/chat/history?limit=500")
    all_entries = all_history_data.get("history", []) if all_history_data else []

    # Get unique session IDs for dropdown
    available_sessions = list({e.get("session_id", "unknown") for e in all_entries})
    available_sessions.sort()

    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input(
            "🔍 Search questions/answers:",
            placeholder="e.g. budget, proposal, executive...",
        )
    with col2:
        # Show dropdown of real session IDs instead of free text
        session_options = ["All Sessions"] + available_sessions
        selected_session = st.selectbox(
            "📋 Filter by Session:",
            options=session_options,
            help="Select a session to filter, or keep 'All Sessions'",
        )

    limit = st.slider("Show last N interactions", 5, 100, 20)

    # Apply filters directly (no button needed)
    filtered_history = all_entries[:limit]  # already most-recent-first

    # Apply session filter
    if selected_session != "All Sessions":
        filtered_history = [
            e for e in filtered_history
            if e.get("session_id") == selected_session
        ]

    # Apply search filter
    if search_query.strip():
        search_lower = search_query.strip().lower()
        filtered_history = [
            e for e in filtered_history
            if search_lower in e["question"].lower() or search_lower in e["answer"].lower()
        ]

    # Show results count
    if search_query.strip() or selected_session != "All Sessions":
        st.info(f"🔍 Showing **{len(filtered_history)}** matching interaction(s)")
    else:
        st.info(f"📊 Showing last **{len(filtered_history)}** interaction(s)")

    if filtered_history:
        # Export button
        export_data = []
        for entry in filtered_history:
            export_data.append(f"Timestamp: {entry['timestamp']}")
            export_data.append(f"Session: {entry.get('session_id', 'Unknown')}")
            export_data.append(f"Question: {entry['question']}")
            export_data.append(f"Answer: {entry['answer']}")
            if entry.get("sources"):
                export_data.append(f"Sources: {', '.join(entry['sources'])}")
            export_data.append("-" * 80)

        st.download_button(
            "📥 Export Chat History",
            data="\n".join(export_data),
            file_name=f"chat_history_{len(filtered_history)}_entries.txt",
            mime="text/plain",
        )

        for idx, entry in enumerate(filtered_history):
            formatted_ts = format_timestamp_for_display(entry["timestamp"])
            session_info = entry.get("session_id", "Unknown")
            q_preview = entry["question"][:55] + "..." if len(entry["question"]) > 55 else entry["question"]
            header = f"🕐 {formatted_ts} | 👤 {session_info} | {q_preview}"

            with st.expander(header):
                st.write(f"**❓ Question:** {entry['question']}")
                st.divider()
                st.write("**💬 Answer:**")
                st.markdown(entry["answer"])

                answer_length = len(entry["answer"])
                word_count = len(entry["answer"].split())
                st.caption(f"📊 {answer_length} characters · {word_count} words")

                if st.button("📋 Copy Answer", key=f"copy_history_{idx}_{session_info}"):
                    st.code(entry["answer"], language=None)

                col1, col2 = st.columns(2)
                with col1:
                    if entry.get("sources"):
                        st.write(f"**📎 Sources:** {', '.join(entry['sources'])}")
                with col2:
                    chunks = entry.get("retrieval_info", {}).get("chunks_used")
                    if chunks:
                        st.write(f"**🧩 Chunks Used:** {chunks}")

                if entry.get("retrieval_info", {}).get("citations"):
                    st.write("**🔖 Citations:**")
                    for citation in entry["retrieval_info"]["citations"]:
                        st.caption(f"• {citation}")
    else:
        if all_entries:
            st.warning("⚠️ No results match your search/filter. Try clearing the filters.")
        else:
            st.info("💬 No chat history yet. Start chatting in the **Chat / Q&A** tab!")

    st.divider()

    with st.expander("⚠️ Danger Zone"):
        st.warning("These actions are irreversible.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat History Logs", type="secondary"):
                result = api_delete("/chat/history/clear")
                if result:
                    st.success("Chat history cleared.")
        with col2:
            if st.button("🗑️ Clear Knowledge Base", type="secondary"):
                result = api_post("/documents/clear")
                if result:
                    st.success("Knowledge base cleared.")
                    st.rerun()
