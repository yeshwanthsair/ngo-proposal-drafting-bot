# Week 1 Test Validation Proof
**Project:** NGO Proposal Drafting Bot (PRJ-032)  
**Student:** Yeshwanth Sai R | Reg No: 411723104059

---

## Test Suite Overview

File: `tests/test_week1.py`  
Total Test Cases: **20**

---

## Test Categories

### 1. Document Parser Tests (`TestDocumentParser`) — 7 tests

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_parse_txt_file` | Parse a .txt file | Returns non-empty string with correct content |
| `test_chunk_text_creates_documents` | Chunk text into LangChain Documents | Returns list of Documents with metadata |
| `test_chunk_text_respects_size` | Chunks don't exceed max size | Each chunk ≤ chunk_size × 1.2 chars |
| `test_chunk_metadata_has_total_chunks` | Metadata includes total count | `total_chunks` matches actual count |
| `test_parse_and_chunk_pipeline` | Full parse → chunk pipeline | Returns non-empty Document list |
| `test_unsupported_file_type_raises_error` | Reject .xyz files | Raises `ValueError` |
| `test_empty_file_raises_error` | Reject whitespace-only files | Raises `ValueError` |

### 2. Knowledge Base Tests (`TestKnowledgeBase`) — 8 tests

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_kb_initializes` | KB creates without error | Not None, embeddings loaded |
| `test_add_documents` | Add chunks to ChromaDB | Returns correct count |
| `test_stats_after_adding_documents` | Stats reflect added docs | Correct document/chunk counts |
| `test_similarity_search_returns_results` | Search returns results | List of (Document, score) tuples |
| `test_similarity_search_relevance` | Search returns relevant content | Budget query returns budget content |
| `test_get_retriever` | Retriever object returned | Not None |
| `test_empty_kb_stats` | Empty KB stats | 0 documents, 0 chunks |
| `test_add_empty_documents_list` | Add empty list | Returns 0 |

### 3. API Endpoint Tests (`TestAPIEndpoints`) — 8 tests

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_root_endpoint` | GET / | 200, project info JSON |
| `test_health_endpoint` | GET /health | 200, status: healthy |
| `test_documents_stats_endpoint` | GET /api/v1/documents/stats | 200, stats structure |
| `test_documents_list_endpoint` | GET /api/v1/documents/list | 200, documents list |
| `test_upload_txt_document` | POST /api/v1/documents/upload | 200, success: true, chunks > 0 |
| `test_upload_unsupported_format` | Upload .xyz file | 400 Bad Request |
| `test_chat_health_endpoint` | GET /api/v1/chat/health | 200, status: ok |
| `test_chat_ask_missing_question` | POST /api/v1/chat/ask with empty question | 422 Validation Error |

### 4. Sample Documents Tests (`TestSampleDocuments`) — 3 tests

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_sample_docs_exist` | data/sample_docs/ has .txt files | At least 1 file found |
| `test_sample_docs_parseable` | All sample docs parse without error | Non-empty chunk lists |
| `test_sample_docs_have_ngo_content` | Docs contain NGO keywords | proposal, budget, ngo, grant found |

---

## How to Run Tests

```bash
# Install dependencies first
pip install -r requirements.txt

# Run all Week 1 tests
pytest tests/test_week1.py -v

# Run specific test class
pytest tests/test_week1.py::TestDocumentParser -v
pytest tests/test_week1.py::TestKnowledgeBase -v
pytest tests/test_week1.py::TestAPIEndpoints -v
```

---

## Week 1 Deliverables Checklist

- [x] Knowledge base created (ChromaDB)
- [x] Document upload and parsing (PDF, TXT, DOCX)
- [x] Text chunking with overlap
- [x] Embedding generation (sentence-transformers)
- [x] Basic chat/Q&A interface (Streamlit)
- [x] FastAPI backend with REST endpoints
- [x] Sample NGO documents (3 files)
- [x] Test cases (20 tests across 4 categories)
- [x] README with setup instructions
