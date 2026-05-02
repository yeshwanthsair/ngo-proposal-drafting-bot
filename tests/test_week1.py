"""
Week 1 Test Cases - NGO Proposal Drafting Bot
Tests: document loading, chunking, vector store, and API endpoints.

Run with: pytest tests/test_week1.py -v
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Test Data ──────────────────────────────────────────────────────────────────

SAMPLE_TEXT = """
NGO PROPOSAL GUIDE

Executive Summary
An executive summary provides a brief overview of the entire proposal.
It should be no more than one page and cover the key points.

Problem Statement
The problem statement describes the issue your project will address.
Use data and evidence to support your claims.

Budget Planning
The budget should include all costs: personnel, equipment, travel, and overhead.
Overhead costs are typically 10-20% of direct costs.
"""

SAMPLE_NGO_QUESTION = "What should be included in an executive summary?"


# ── Tests: Document Parser ─────────────────────────────────────────────────────

class TestDocumentParser:
    """Test document parsing and chunking functionality."""

    def test_parse_txt_file(self):
        """Test that TXT files are parsed correctly."""
        from backend.services.document_parser import parse_txt

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(SAMPLE_TEXT)
            temp_path = f.name

        try:
            result = parse_txt(temp_path)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "NGO PROPOSAL GUIDE" in result
        finally:
            os.unlink(temp_path)

    def test_chunk_text_creates_documents(self):
        """Test that text chunking creates LangChain Document objects."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test_doc.txt", chunk_size=200, chunk_overlap=50)

        assert len(docs) > 0
        for doc in docs:
            assert hasattr(doc, "page_content")
            assert hasattr(doc, "metadata")
            assert doc.metadata["source"] == "test_doc.txt"
            assert "chunk_index" in doc.metadata

    def test_chunk_text_respects_size(self):
        """Test that chunks don't exceed the specified size."""
        from backend.services.document_parser import chunk_text

        chunk_size = 300
        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=chunk_size, chunk_overlap=50)

        for doc in docs:
            # Allow slight overflow due to splitter behavior
            assert len(doc.page_content) <= chunk_size * 1.2, \
                f"Chunk too large: {len(doc.page_content)} chars"

    def test_chunk_metadata_has_total_chunks(self):
        """Test that metadata includes total chunk count."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=200, chunk_overlap=50)
        total = len(docs)

        for doc in docs:
            assert doc.metadata["total_chunks"] == total

    def test_parse_and_chunk_pipeline(self):
        """Test the full parse-and-chunk pipeline."""
        from backend.services.document_parser import parse_and_chunk

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(SAMPLE_TEXT)
            temp_path = f.name

        try:
            docs = parse_and_chunk(temp_path)
            assert len(docs) > 0
            assert all(doc.page_content.strip() for doc in docs)
        finally:
            os.unlink(temp_path)

    def test_unsupported_file_type_raises_error(self):
        """Test that unsupported file types raise ValueError."""
        from backend.services.document_parser import parse_document

        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_document("document.xyz")

    def test_empty_file_raises_error(self):
        """Test that empty files raise ValueError."""
        from backend.services.document_parser import parse_and_chunk

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("   ")  # whitespace only
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="No text content"):
                parse_and_chunk(temp_path)
        finally:
            os.unlink(temp_path)


# ── Tests: Knowledge Base ──────────────────────────────────────────────────────

class TestKnowledgeBase:
    """Test ChromaDB knowledge base operations."""

    @pytest.fixture
    def temp_kb(self, tmp_path):
        """Create a temporary knowledge base for testing."""
        from backend.services.knowledge_base import KnowledgeBase
        kb = KnowledgeBase(persist_dir=str(tmp_path / "test_chroma"))
        yield kb
        # Cleanup
        try:
            kb.delete_collection()
        except Exception:
            pass

    def test_kb_initializes(self, temp_kb):
        """Test that knowledge base initializes without errors."""
        assert temp_kb is not None
        assert temp_kb.embeddings is not None

    def test_add_documents(self, temp_kb):
        """Test adding documents to the knowledge base."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=300, chunk_overlap=50)
        count = temp_kb.add_documents(docs)

        assert count == len(docs)
        assert count > 0

    def test_stats_after_adding_documents(self, temp_kb):
        """Test that stats reflect added documents."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "ngo_guide.txt", chunk_size=300, chunk_overlap=50)
        temp_kb.add_documents(docs)

        stats = temp_kb.get_stats()
        assert stats["total_chunks"] == len(docs)
        assert stats["total_documents"] == 1
        assert "ngo_guide.txt" in stats["documents"]

    def test_similarity_search_returns_results(self, temp_kb):
        """Test that similarity search returns relevant results."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=300, chunk_overlap=50)
        temp_kb.add_documents(docs)

        results = temp_kb.similarity_search("executive summary proposal", k=2)

        assert len(results) > 0
        assert len(results) <= 2
        # Each result is (Document, score)
        doc, score = results[0]
        assert hasattr(doc, "page_content")
        assert isinstance(score, float)

    def test_similarity_search_relevance(self, temp_kb):
        """Test that search returns relevant content."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=300, chunk_overlap=50)
        temp_kb.add_documents(docs)

        results = temp_kb.similarity_search("budget overhead costs", k=3)

        # At least one result should mention budget
        contents = [doc.page_content.lower() for doc, _ in results]
        assert any("budget" in c or "cost" in c or "overhead" in c for c in contents), \
            "Search should return budget-related content"

    def test_get_retriever(self, temp_kb):
        """Test that retriever is returned correctly."""
        from backend.services.document_parser import chunk_text

        docs = chunk_text(SAMPLE_TEXT, "test.txt", chunk_size=300, chunk_overlap=50)
        temp_kb.add_documents(docs)

        retriever = temp_kb.get_retriever(k=2)
        assert retriever is not None

    def test_empty_kb_stats(self, temp_kb):
        """Test stats on empty knowledge base."""
        stats = temp_kb.get_stats()
        assert stats["total_chunks"] == 0
        assert stats["total_documents"] == 0

    def test_add_empty_documents_list(self, temp_kb):
        """Test adding empty list returns 0."""
        count = temp_kb.add_documents([])
        assert count == 0


# ── Tests: API Endpoints ───────────────────────────────────────────────────────

class TestAPIEndpoints:
    """
    Integration tests for FastAPI endpoints.
    Requires the FastAPI app to be importable (not necessarily running).
    """

    @pytest.fixture
    def client(self, tmp_path, monkeypatch):
        """Create a test client with isolated ChromaDB."""
        monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "test_chroma"))
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.setenv("GOOGLE_API_KEY", "test_key_placeholder")

        # Reset singleton
        import backend.services.knowledge_base as kb_module
        kb_module._kb_instance = None

        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns project info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "NGO Proposal Drafting Bot"
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_documents_stats_endpoint(self, client):
        """Test document stats endpoint returns valid structure."""
        response = client.get("/api/v1/documents/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_chunks" in data
        assert "collection_name" in data

    def test_documents_list_endpoint(self, client):
        """Test document list endpoint."""
        response = client.get("/api/v1/documents/list")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert isinstance(data["documents"], list)

    def test_upload_txt_document(self, client):
        """Test uploading a TXT document."""
        file_content = SAMPLE_TEXT.encode("utf-8")
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_ngo.txt", file_content, "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["filename"] == "test_ngo.txt"
        assert data["chunks_created"] > 0

    def test_upload_unsupported_format(self, client):
        """Test that unsupported file formats are rejected."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.xyz", b"some content", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_chat_health_endpoint(self, client):
        """Test chat health endpoint."""
        response = client.get("/api/v1/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_chat_ask_missing_question(self, client):
        """Test that empty question is rejected."""
        response = client.post("/api/v1/chat/ask", json={"question": ""})
        assert response.status_code == 422  # Validation error


# ── Tests: Sample Documents ────────────────────────────────────────────────────

class TestSampleDocuments:
    """Test that sample documents exist and are parseable."""

    def test_sample_docs_exist(self):
        """Test that sample documents are present."""
        sample_dir = Path("./data/sample_docs")
        assert sample_dir.exists(), "data/sample_docs directory should exist"

        txt_files = list(sample_dir.glob("*.txt"))
        assert len(txt_files) >= 1, "At least one sample .txt file should exist"

    def test_sample_docs_parseable(self):
        """Test that sample documents can be parsed."""
        from backend.services.document_parser import parse_and_chunk

        sample_dir = Path("./data/sample_docs")
        for txt_file in sample_dir.glob("*.txt"):
            docs = parse_and_chunk(str(txt_file))
            assert len(docs) > 0, f"Sample file {txt_file.name} should produce chunks"

    def test_sample_docs_have_ngo_content(self):
        """Test that sample documents contain NGO-relevant content."""
        from backend.services.document_parser import parse_txt

        sample_dir = Path("./data/sample_docs")
        all_text = ""
        for txt_file in sample_dir.glob("*.txt"):
            all_text += parse_txt(str(txt_file)).lower()

        ngo_keywords = ["proposal", "budget", "ngo", "grant", "objective"]
        for keyword in ngo_keywords:
            assert keyword in all_text, f"Sample docs should contain '{keyword}'"


# ── Run tests ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
