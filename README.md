# NGO Proposal Drafting Bot

**Student:** Yeshwanth Sai R | **Reg No:** 411723104059 | **Project Code:** PRJ-032

An AI-powered tool that helps NGOs draft grant proposals and project documents using FastAPI, LangChain, ChromaDB, and Streamlit.

---

## 🌐 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yeshwanthsair-ngo-proposal-drafting-bot-frontendapp-wz0xku.streamlit.app/)

👉 **Live App:** https://yeshwanthsair-ngo-proposal-drafting-bot-frontendapp-wz0xku.streamlit.app/

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Pull the LLM Model
```bash
ollama pull tinyllama
```

### 3. Start the Backend (Terminal 1)
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the Frontend (Terminal 2)
```bash
streamlit run frontend/app.py --server.port 8501
```

### 5. Open the App
- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 📋 Features by Week

### ✅ Week 1 — Foundation
- Document upload (PDF, TXT, DOCX)
- ChromaDB vector store with semantic search
- Basic Chat / Q&A interface
- Ollama (TinyLlama) local LLM integration
- HuggingFace sentence-transformers embeddings

### ✅ Week 2 — Retrieval & Admin
- Improved retrieval with relevance scoring
- Chunk-level citations with source attribution
- NGO-specific prompt tuning
- Edge case handling (greetings, off-topic, empty queries)
- Chat history logging (JSON)
- Admin panel with KB refresh workflow
- Human-readable timestamps

### ✅ Week 3 — UX, Memory & Proposal Generator
- **Conversation Memory** — context-aware multi-turn chat
- **Proposal Draft Generator** — generate full NGO proposals from form inputs
- **Section Generator** — generate individual sections (Executive Summary, Budget, M&E, etc.)
- **Export** — download proposals as TXT or Markdown
- **Checklist Generator** — submission checklist for grant proposals
- **Access Control** — admin login with password protection
- **Session Management** — track active sessions and message counts
- **Improved Chat UX** — memory toggle, clear memory button

---

## 🏗️ Project Structure

```
NGO_Proposal_Drafting_Bot/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── routes/
│   │   ├── chat.py                # Chat, memory, admin endpoints
│   │   ├── documents.py           # Document upload/management
│   │   └── proposals.py           # Proposal generation endpoints (Week 3)
│   ├── services/
│   │   ├── knowledge_base.py      # ChromaDB vector store
│   │   ├── llm_service.py         # Ollama LLM + prompts
│   │   ├── retrieval_service.py   # Retrieval with citations
│   │   ├── chat_logger.py         # Chat history logging
│   │   ├── document_parser.py     # PDF/TXT/DOCX parsing
│   │   ├── proposal_generator.py  # NGO proposal templates (Week 3)
│   │   └── session_manager.py     # Session & access control (Week 3)
│   └── utils/
│       └── datetime_utils.py      # Human-readable timestamps
├── frontend/
│   └── app.py                     # Streamlit UI (all pages)
├── data/
│   ├── sample_docs/               # Sample NGO documents
│   └── uploads/                   # Temp upload directory
├── logs/
│   └── chat_history.json          # Chat interaction logs
├── chroma_db/                     # ChromaDB vector store (auto-created)
├── tests/
│   ├── test_week1.py
│   ├── test_week2.py
│   └── test_week3.py
├── .env                           # Environment variables (never commit)
├── .env.example                   # Example env file
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration (.env)

```env
# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_MODEL=tinyllama
OLLAMA_BASE_URL=http://localhost:11434

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Week 3: Admin Access
ADMIN_PASSWORD=admin123

# Debug
DEBUG=True
```

---

## 🧪 Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Week-specific tests
python -m pytest tests/test_week1.py -v
python -m pytest tests/test_week2.py -v
python -m pytest tests/test_week3.py -v
```

---

## 📱 Application Pages

| Page | Description |
|------|-------------|
| 💬 Chat / Q&A | Ask questions, conversation memory, citations |
| ✍️ Draft Proposal | Generate NGO proposals from form inputs |
| 📁 Upload Documents | Upload PDF/TXT/DOCX to knowledge base |
| 📋 Knowledge Base | View, preview, delete indexed documents |
| 🔧 Admin Panel | Login, sessions, chat history, system tools |

---

## 🔐 Admin Access

Default password: **admin123**

Change in `.env`:
```env
ADMIN_PASSWORD=Yeshwanth@2006
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI |
| Frontend | Streamlit |
| LLM | Ollama (TinyLlama) |
| Vector DB | ChromaDB |
| Embeddings | HuggingFace sentence-transformers |
| Document Parsing | LangChain, pypdf, python-docx |
| Framework | LangChain |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/ask` | Ask a question (with memory) |
| GET | `/api/v1/chat/history` | Get chat history |
| POST | `/api/v1/chat/admin/login` | Admin login |
| POST | `/api/v1/chat/admin/refresh` | Refresh knowledge base |
| POST | `/api/v1/chat/session/clear` | Clear conversation memory |
| GET | `/api/v1/chat/sessions` | List active sessions |
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents/list` | List documents |
| DELETE | `/api/v1/documents/delete/{filename}` | Delete document |
| POST | `/api/v1/proposals/generate` | Generate proposal section |
| POST | `/api/v1/proposals/checklist` | Generate submission checklist |
| GET | `/api/v1/proposals/sections` | List available sections |

---

*NGO Proposal Drafting Bot | PRJ-032 | Yeshwanth Sai R | 411723104059*
