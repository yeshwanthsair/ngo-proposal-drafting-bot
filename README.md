# NGO Proposal Drafting Bot

**Project Code:** PRJ-032  
**Student:** Yeshwanth Sai R  
**Reg No:** 411723104059  
**Department:** CSE, PSVPEC  

---

## Overview

An AI-powered tool that helps NGOs draft grant proposals and project documents from program details. Built with FastAPI, LangChain, Streamlit, and ChromaDB.

---

## Features

- **Template-based drafting** – Generate structured proposals from input details
- **Section/Chapter planner** – Organize proposals into logical sections
- **Editable outputs** – Review and edit generated content
- **Checklist generation** – Auto-generate submission checklists
- **Exportable final text** – Download proposals as `.txt` or `.docx`
- **Knowledge base Q&A** – Chat with uploaded NGO documents

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | FastAPI (Python)                  |
| AI/LLM    | LangChain + Google Gemini / OpenAI|
| Vector DB | ChromaDB                          |
| Frontend  | Streamlit                         |
| Embeddings| sentence-transformers             |

---

## Project Structure

```
ngo-proposal-bot/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   ├── chat.py          # Chat/Q&A endpoints
│   │   ├── documents.py     # Document upload/parse endpoints
│   │   └── proposals.py     # Proposal generation endpoints
│   ├── services/
│   │   ├── knowledge_base.py  # ChromaDB vector store logic
│   │   ├── llm_service.py     # LangChain LLM integration
│   │   └── document_parser.py # PDF/DOCX parsing
│   └── models/
│       └── schemas.py         # Pydantic models
├── frontend/
│   └── app.py               # Streamlit UI
├── data/
│   └── sample_docs/         # Sample NGO documents
├── tests/
│   ├── test_week1.py        # Week 1 test cases
│   └── test_data/
├── .env.example             # Environment variable template
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ngo-proposal-bot
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your API key
```

### 5. Run the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 6. Run the frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

### 7. Access the app
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

## Week-by-Week Progress

### ✅ Week 1 – Knowledge Base & Basic Chat
- [x] Project structure setup
- [x] Document upload and parsing (PDF, TXT, DOCX)
- [x] ChromaDB vector store integration
- [x] Text chunking and embedding
- [x] Basic Q&A chat interface
- [x] FastAPI endpoints for documents and chat
- [x] Streamlit UI with chat and upload tabs

### 🔲 Week 2 – Retrieval, Prompt Tuning & Citations
- [ ] Improved retrieval with citations
- [ ] Prompt engineering for NGO context
- [ ] Admin document refresh workflow
- [ ] Edge case and fallback handling

### 🔲 Week 3 – UX, History & Final Polish
- [ ] Chat history and logging
- [ ] Proposal generation with templates
- [ ] Export to DOCX
- [ ] Checklist generation
- [ ] Final documentation and demo

---

## Test Cases

See `tests/test_week1.py` for automated test cases covering:
- Document loading and chunking
- Vector store operations
- API endpoint responses
- Q&A baseline flow

---

## Important Notes

- API keys are stored in `.env` (never committed to Git)
- Uses free `sentence-transformers` embeddings (no paid API needed for embeddings)
- Sample NGO documents included in `data/sample_docs/`
