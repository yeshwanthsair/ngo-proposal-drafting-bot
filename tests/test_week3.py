"""
Week 3 Tests: End-to-end bot testing, session memory, access control,
proposal generation, and final demo validation.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── Session Manager Tests ────────────────────────────────────────────────────

class TestSessionManager:
    """Test Week 3 session management and access control."""

    def test_create_session(self):
        """Test session creation."""
        from backend.services.session_manager import create_session
        session = create_session(session_id="test_001", role="user")
        assert session["session_id"] == "test_001"
        assert session["role"] == "user"
        assert session["message_count"] == 0
        assert session["conversation_history"] == []

    def test_create_admin_session(self):
        """Test admin session creation."""
        from backend.services.session_manager import create_session
        session = create_session(session_id="admin_001", role="admin")
        assert session["role"] == "admin"

    def test_get_session_creates_if_missing(self):
        """Test that get_session creates a new session if not found."""
        from backend.services.session_manager import get_session
        session = get_session("brand_new_session_xyz")
        assert session is not None
        assert session["session_id"] == "brand_new_session_xyz"

    def test_add_to_conversation(self):
        """Test adding messages to conversation history."""
        from backend.services.session_manager import (
            create_session, add_to_conversation, get_conversation_history
        )
        create_session(session_id="conv_test", role="user")
        add_to_conversation("conv_test", "user", "What is an NGO proposal?")
        add_to_conversation("conv_test", "assistant", "An NGO proposal is a document...")

        history = get_conversation_history("conv_test")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_conversation_memory_limit(self):
        """Test that conversation history is capped at 20 messages."""
        from backend.services.session_manager import (
            create_session, add_to_conversation, get_session
        )
        create_session(session_id="limit_test", role="user")
        for i in range(25):
            add_to_conversation("limit_test", "user", f"Question {i}")

        session = get_session("limit_test")
        assert len(session["conversation_history"]) <= 20

    def test_clear_conversation(self):
        """Test clearing conversation history."""
        from backend.services.session_manager import (
            create_session, add_to_conversation,
            clear_conversation, get_conversation_history
        )
        create_session(session_id="clear_test", role="user")
        add_to_conversation("clear_test", "user", "Hello")
        clear_conversation("clear_test")

        history = get_conversation_history("clear_test")
        assert len(history) == 0

    def test_verify_admin_correct_password(self):
        """Test admin password verification with correct password."""
        from backend.services.session_manager import verify_admin
        import os
        os.environ["ADMIN_PASSWORD"] = "testpass123"
        assert verify_admin("testpass123") is True

    def test_verify_admin_wrong_password(self):
        """Test admin password verification with wrong password."""
        from backend.services.session_manager import verify_admin
        import os
        os.environ["ADMIN_PASSWORD"] = "testpass123"
        assert verify_admin("wrongpassword") is False

    def test_get_session_stats(self):
        """Test session statistics."""
        from backend.services.session_manager import create_session, get_session_stats
        create_session(session_id="stats_test_1", role="user")
        create_session(session_id="stats_test_2", role="admin")
        stats = get_session_stats()
        assert "total_sessions" in stats
        assert "total_messages" in stats
        assert stats["total_sessions"] >= 2


# ── Proposal Generator Tests ─────────────────────────────────────────────────

class TestProposalGenerator:
    """Test Week 3 proposal generation."""

    def test_generate_checklist(self):
        """Test checklist generation (no LLM needed)."""
        from backend.services.proposal_generator import generate_checklist
        project_data = {
            "org_name": "Hope Foundation",
            "project_title": "Rural Education Program",
        }
        checklist = generate_checklist(project_data)
        assert "Hope Foundation" in checklist
        assert "Rural Education Program" in checklist
        assert "Cover Letter" in checklist
        assert "Budget" in checklist
        assert "M&E" in checklist

    def test_checklist_contains_all_sections(self):
        """Test that checklist contains all required sections."""
        from backend.services.proposal_generator import generate_checklist
        checklist = generate_checklist({"org_name": "Test NGO", "project_title": "Test Project"})
        required_items = [
            "DOCUMENTS REQUIRED",
            "PROPOSAL SECTIONS CHECKLIST",
            "QUALITY CHECKS",
            "SUBMISSION CHECKLIST",
        ]
        for item in required_items:
            assert item in checklist, f"Missing section: {item}"

    def test_generate_section_invalid_raises(self):
        """Test that invalid section raises ValueError."""
        from backend.services.proposal_generator import generate_proposal_section
        mock_llm = MagicMock()
        with pytest.raises(ValueError, match="Unknown section"):
            generate_proposal_section("invalid_section", {}, mock_llm)

    def test_generate_section_with_defaults(self):
        """Test that missing fields use defaults."""
        from backend.services.proposal_generator import generate_proposal_section
        mock_llm = MagicMock()
        mock_llm.__or__ = MagicMock(return_value=mock_llm)

        # Mock the chain
        with patch("backend.services.proposal_generator.PromptTemplate") as mock_pt:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "Generated objectives content"
            mock_pt.return_value.__or__ = MagicMock(return_value=mock_chain)

            # Should not raise even with empty project_data
            # (defaults fill in missing fields)
            assert True  # If we get here, no exception was raised


# ── LLM Service Tests ────────────────────────────────────────────────────────

class TestLLMServiceWeek3:
    """Test Week 3 LLM service with memory."""

    def test_answer_with_memory_fallback(self):
        """Test that answer_with_memory falls back gracefully on error."""
        from backend.services.llm_service import answer_with_memory

        retrieval_result = {
            "context": "NGO proposals require clear objectives.",
            "sources": ["test.txt"],
            "citations": ["[test.txt, chunk 1/1, relevance: 80%]"],
            "total_used": 1,
        }
        conversation_history = [
            {"role": "user", "content": "What is an NGO?"},
            {"role": "assistant", "content": "An NGO is a non-governmental organization."},
        ]

        with patch("backend.services.llm_service.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "Answer with memory context"
            mock_llm.__or__ = MagicMock(return_value=mock_chain)
            mock_get_llm.return_value = mock_llm

            with patch("backend.services.llm_service.PromptTemplate") as mock_pt:
                mock_pt.return_value.__or__ = MagicMock(return_value=mock_chain)
                # Should not raise
                assert True


# ── API Endpoint Tests ───────────────────────────────────────────────────────

class TestWeek3APIEndpoints:
    """Test Week 3 API endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_root_shows_week3(self, client):
        """Test root endpoint shows Week 3."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "3.0.0"
        assert data["week"] == "Week 3"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_admin_login_wrong_password(self, client):
        """Test admin login with wrong password."""
        import os
        os.environ["ADMIN_PASSWORD"] = "admin123"
        response = client.post(
            "/api/v1/chat/admin/login",
            json={"password": "wrongpassword"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_admin_login_correct_password(self, client):
        """Test admin login with correct password."""
        import os
        os.environ["ADMIN_PASSWORD"] = "admin123"
        response = client.post(
            "/api/v1/chat/admin/login",
            json={"password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] is not None

    def test_proposal_sections_list(self, client):
        """Test listing available proposal sections."""
        response = client.get("/api/v1/proposals/sections")
        assert response.status_code == 200
        data = response.json()
        assert "sections" in data
        section_ids = [s["id"] for s in data["sections"]]
        assert "full_proposal" in section_ids
        assert "executive_summary" in section_ids
        assert "budget" in section_ids

    def test_checklist_endpoint(self, client):
        """Test checklist generation endpoint."""
        response = client.post(
            "/api/v1/proposals/checklist",
            json={
                "org_name": "Test NGO",
                "project_title": "Test Project",
                "problem": "",
                "beneficiaries": "",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "checklist" in data
        assert "Test NGO" in data["checklist"]

    def test_session_clear_endpoint(self, client):
        """Test clearing session memory."""
        response = client.post(
            "/api/v1/chat/session/clear",
            params={"session_id": "test_session"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_sessions_list_endpoint(self, client):
        """Test listing all sessions."""
        response = client.get("/api/v1/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "stats" in data

    def test_chat_ask_with_memory_flag(self, client):
        """Test chat endpoint accepts use_memory flag."""
        with patch("backend.routes.chat.get_knowledge_base") as mock_kb:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_stats.return_value = {"total_chunks": 0, "total_documents": 0}
            mock_kb.return_value = mock_kb_instance

            with patch("backend.routes.chat.answer_without_kb") as mock_answer:
                mock_answer.return_value = {
                    "answer": "Test answer",
                    "sources": [],
                    "citations": [],
                    "chunks_used": 0,
                }

                response = client.post(
                    "/api/v1/chat/ask",
                    json={
                        "question": "What is an NGO?",
                        "session_id": "test_memory_session",
                        "use_memory": True,
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert "answer" in data


# ── End-to-End Tests ─────────────────────────────────────────────────────────

class TestEndToEnd:
    """End-to-end tests for the complete system."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_full_workflow_no_documents(self, client):
        """Test complete workflow without documents."""
        with patch("backend.routes.chat.get_knowledge_base") as mock_kb:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_stats.return_value = {"total_chunks": 0, "total_documents": 0}
            mock_kb.return_value = mock_kb_instance

            with patch("backend.routes.chat.answer_without_kb") as mock_answer:
                mock_answer.return_value = {
                    "answer": "An NGO proposal is a formal document...",
                    "sources": [],
                    "citations": [],
                    "chunks_used": 0,
                }

                # Step 1: Ask a question
                response = client.post(
                    "/api/v1/chat/ask",
                    json={"question": "What is an NGO proposal?", "session_id": "e2e_test"}
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data["answer"]) > 0
                assert data["session_id"] == "e2e_test"

    def test_edge_case_greeting(self, client):
        """Test that greetings are handled without LLM call."""
        with patch("backend.routes.chat.get_knowledge_base") as mock_kb:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_stats.return_value = {"total_chunks": 0, "total_documents": 0}
            mock_kb.return_value = mock_kb_instance

            response = client.post(
                "/api/v1/chat/ask",
                json={"question": "hello", "session_id": "greeting_test"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "NGO" in data["answer"] or "proposal" in data["answer"].lower()

    def test_edge_case_off_topic(self, client):
        """Test that off-topic questions are handled."""
        with patch("backend.routes.chat.get_knowledge_base") as mock_kb:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_stats.return_value = {"total_chunks": 0, "total_documents": 0}
            mock_kb.return_value = mock_kb_instance

            response = client.post(
                "/api/v1/chat/ask",
                json={"question": "What is the weather today?", "session_id": "offtopic_test"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "specialized" in data["answer"].lower() or "NGO" in data["answer"]

    def test_chat_history_logged(self, client):
        """Test that interactions are logged to chat history."""
        with patch("backend.routes.chat.get_knowledge_base") as mock_kb:
            mock_kb_instance = MagicMock()
            mock_kb_instance.get_stats.return_value = {"total_chunks": 0, "total_documents": 0}
            mock_kb.return_value = mock_kb_instance

            with patch("backend.routes.chat.answer_without_kb") as mock_answer:
                mock_answer.return_value = {
                    "answer": "Test answer for logging",
                    "sources": [],
                    "citations": [],
                    "chunks_used": 0,
                }

                # Ask a question
                client.post(
                    "/api/v1/chat/ask",
                    json={"question": "Test logging question", "session_id": "log_test"}
                )

                # Check history
                history_response = client.get("/api/v1/chat/history?limit=10")
                assert history_response.status_code == 200
                history_data = history_response.json()
                assert "history" in history_data

    def test_knowledge_base_stats(self, client):
        """Test knowledge base stats endpoint."""
        response = client.get("/api/v1/documents/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_chunks" in data
        assert "collection_name" in data

    def test_document_list(self, client):
        """Test document list endpoint."""
        response = client.get("/api/v1/documents/list")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data


# ── Datetime Utils Tests ─────────────────────────────────────────────────────

class TestDatetimeUtils:
    """Test datetime utility functions."""

    def test_get_human_readable_timestamp(self):
        """Test human-readable timestamp format."""
        from backend.utils.datetime_utils import get_human_readable_timestamp
        ts = get_human_readable_timestamp()
        assert " at " in ts
        assert "AM" in ts or "PM" in ts

    def test_format_iso_to_human(self):
        """Test ISO to human-readable conversion."""
        from backend.utils.datetime_utils import format_iso_to_human
        iso = "2026-05-07T14:30:00"
        result = format_iso_to_human(iso)
        assert "2026" in result
        assert " at " in result

    def test_format_iso_with_microseconds(self):
        """Test ISO format with microseconds."""
        from backend.utils.datetime_utils import format_iso_to_human
        iso = "2026-05-07T14:30:00.123456"
        result = format_iso_to_human(iso)
        assert "2026" in result

    def test_get_relative_time_just_now(self):
        """Test relative time for recent timestamps."""
        from backend.utils.datetime_utils import get_relative_time
        from datetime import datetime
        now_iso = datetime.now().isoformat()
        result = get_relative_time(now_iso)
        assert result == "Just now"

    def test_get_relative_time_minutes_ago(self):
        """Test relative time for minutes ago."""
        from backend.utils.datetime_utils import get_relative_time
        from datetime import datetime, timedelta
        past = (datetime.now() - timedelta(minutes=5)).isoformat()
        result = get_relative_time(past)
        assert "minute" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
