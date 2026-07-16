"""
Week 2 Test Cases - NGO Proposal Drafting Bot
Tests: retrieval with citations, edge cases, chat logging, admin endpoints.

Run with: pytest tests/test_week2.py -v
"""
import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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

Monitoring and Evaluation
M&E framework should include KPIs, data collection methods, and reporting schedule.
"""


# ── Tests: Retrieval Service ───────────────────────────────────────────────────

class TestRetrievalService:
    """Test Week 2 improved retrieval with citations."""

    @pytest.fixture
    def temp_kb(self, tmp_path):
        from backend.services.knowledge_base import KnowledgeBase
        kb = KnowledgeBase(persist_dir=str(tmp_path / "test_chroma"))
        from backend.services.document_parser import chunk_text
        docs = chunk_text(SAMPLE_TEXT, "test_guide.txt", chunk_size=300, chunk_overlap=50)
        kb.add_documents(docs)
        yield kb
        try:
            kb.delete_collection()
        except Exception:
            pass

    def test_retrieve_with_citations_returns_result(self, temp_kb):
        """Test that retrieval returns proper structure."""
        from backend.services.retrieval_service import retrieve_with_citations
        result = retrieve_with_citations("executive summary", temp_kb, k=3)

        assert "chunks" in result
        assert "citations" in result
        assert "context" in result
        assert "sources" in result
        assert "total_retrieved" in result
        assert "total_used" in result

    def test_retrieve_returns_relevant_chunks(self, temp_kb):
        """Test that retrieval returns relevant content."""
        from backend.services.retrieval_service import retrieve_with_citations
        result = retrieve_with_citations("budget overhead costs", temp_kb, k=3)

        assert result["total_retrieved"] > 0
        if result["total_used"] > 0:
            contents = [c["content"].lower() for c in result["chunks"]]
            assert any("budget" in c or "cost" in c for c in contents)

    def test_citations_format(self, temp_kb):
        """Test that citations are properly formatted."""
        from backend.services.retrieval_service import retrieve_with_citations
        result = retrieve_with_citations("proposal structure", temp_kb, k=3)

        for citation in result["citations"]:
            assert "[" in citation
            assert "]" in citation
            assert "chunk" in citation.lower()

    def test_chunk_metadata_in_result(self, temp_kb):
        """Test that chunks include required metadata."""
        from backend.services.retrieval_service import retrieve_with_citations
        result = retrieve_with_citations("executive summary", temp_kb, k=2)

        for chunk in result["chunks"]:
            assert "content" in chunk
            assert "source" in chunk
            assert "relevance_score" in chunk
            assert "chunk_index" in chunk


# ── Tests: Edge Case Handling ──────────────────────────────────────────────────

class TestEdgeCases:
    """Test Week 2 edge case handling."""

    def test_empty_question_handled(self):
        """Test that very short questions are handled."""
        from backend.services.retrieval_service import handle_edge_cases
        result = handle_edge_cases("hi", {"total_chunks": 0})
        assert result is not None
        assert len(result) > 0

    def test_greeting_handled(self):
        """Test that greetings return friendly response."""
        from backend.services.retrieval_service import handle_edge_cases
        result = handle_edge_cases("hello", {"total_chunks": 5})
        assert result is not None
        assert "assistant" in result.lower() or "hello" in result.lower()

    def test_off_topic_handled(self):
        """Test that off-topic questions are redirected."""
        from backend.services.retrieval_service import handle_edge_cases
        result = handle_edge_cases("what is the weather today", {"total_chunks": 5})
        assert result is not None
        assert "ngo" in result.lower() or "proposal" in result.lower()

    def test_normal_question_passes_through(self):
        """Test that normal NGO questions return None (no edge case)."""
        from backend.services.retrieval_service import handle_edge_cases
        result = handle_edge_cases(
            "What should be included in an executive summary?",
            {"total_chunks": 5}
        )
        assert result is None

    def test_no_docs_document_specific_question(self):
        """Test that document-specific questions with empty KB are handled."""
        from backend.services.retrieval_service import handle_edge_cases
        result = handle_edge_cases(
            "What does the uploaded document say about budget?",
            {"total_chunks": 0}
        )
        assert result is not None
        assert "upload" in result.lower() or "document" in result.lower()


# ── Tests: Chat Logger ─────────────────────────────────────────────────────────

class TestChatLogger:
    """Test Week 2 chat history logging."""

    @pytest.fixture
    def temp_logger(self, tmp_path, monkeypatch):
        import backend.services.chat_logger as logger_module
        monkeypatch.setattr(logger_module, "LOG_DIR", tmp_path / "logs")
        monkeypatch.setattr(logger_module, "LOG_FILE", tmp_path / "logs" / "chat_history.json")
        return logger_module

    def test_log_interaction(self, temp_logger):
        """Test that interactions are logged correctly."""
        temp_logger.log_interaction(
            session_id="test_session",
            question="What is an executive summary?",
            answer="An executive summary is...",
            sources=["ngo_guide.txt"],
        )
        history = temp_logger.get_chat_history()
        assert len(history) == 1
        assert history[0]["question"] == "What is an executive summary?"
        assert history[0]["session_id"] == "test_session"

    def test_get_history_by_session(self, temp_logger):
        """Test filtering history by session ID."""
        temp_logger.log_interaction("session_1", "Q1", "A1", [])
        temp_logger.log_interaction("session_2", "Q2", "A2", [])
        temp_logger.log_interaction("session_1", "Q3", "A3", [])

        session1_history = temp_logger.get_chat_history(session_id="session_1")
        assert len(session1_history) == 2

    def test_get_stats(self, temp_logger):
        """Test chat history statistics."""
        temp_logger.log_interaction("s1", "Q1", "A1", [])
        temp_logger.log_interaction("s2", "Q2", "A2", [])

        stats = temp_logger.get_stats()
        assert stats["total_interactions"] == 2
        assert stats["total_sessions"] == 2

    def test_clear_history(self, temp_logger):
        """Test clearing chat history."""
        temp_logger.log_interaction("s1", "Q1", "A1", [])
        temp_logger.clear_history()
        history = temp_logger.get_chat_history()
        assert len(history) == 0


# ── Tests: Week 2 API Endpoints ────────────────────────────────────────────────

class TestWeek2API:
    """Integration tests for Week 2 API endpoints."""

    @pytest.fixture
    def client(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "test_chroma"))
        monkeypatch.setenv("LLM_PROVIDER", "ollama")

        import backend.services.knowledge_base as kb_module
        kb_module._kb_instance = None

        import backend.services.chat_logger as logger_module
        monkeypatch.setattr(logger_module, "LOG_DIR", tmp_path / "logs")
        monkeypatch.setattr(logger_module, "LOG_FILE", tmp_path / "logs" / "chat_history.json")

        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_chat_health_has_interactions(self, client):
        """Test chat health endpoint includes interaction count."""
        response = client.get("/api/v1/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert "total_interactions_logged" in data

    def test_chat_history_endpoint(self, client):
        """Test chat history endpoint returns proper structure."""
        response = client.get("/api/v1/chat/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "total" in data

    def test_chat_history_stats_endpoint(self, client):
        """Test chat history stats endpoint."""
        response = client.get("/api/v1/chat/history/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_interactions" in data

    def test_admin_refresh_endpoint(self, client):
        """Test admin refresh endpoint."""
        response = client.post("/api/v1/chat/admin/refresh")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_chat_response_has_citations_field(self, client):
        """Test that chat response includes citations field."""
        response = client.post(
            "/api/v1/chat/ask",
            json={"question": "What is an executive summary?", "session_id": "test"}
        )
        # May fail if Ollama not running, just check structure
        if response.status_code == 200:
            data = response.json()
            assert "citations" in data
            assert "chunks_used" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
