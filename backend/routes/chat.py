"""
Week 3: Chat/Q&A routes with conversation memory and access control.
- Conversation memory across turns
- Session-based access control
- Admin login endpoint
- Improved context with history
"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from backend.models.schemas import (
    ChatRequest, ChatResponse,
    AdminLoginRequest, AdminLoginResponse,
)
from backend.services.knowledge_base import get_knowledge_base
from backend.services.llm_service import answer_question, answer_without_kb, answer_with_memory
from backend.services.retrieval_service import retrieve_with_citations, handle_edge_cases
from backend.services.chat_logger import log_interaction, get_chat_history, get_stats, clear_history
from backend.services.session_manager import (
    get_session, add_to_conversation, get_conversation_history,
    clear_conversation, verify_admin, create_session,
    get_all_sessions, get_session_stats,
)
from backend.utils.datetime_utils import get_human_readable_timestamp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question about NGO proposals and grant writing.
    Week 3: Conversation memory, session tracking.
    """
    logger.info(f"Question: {request.question[:80]}...")

    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()

        # Ensure session exists
        session = get_session(request.session_id)

        # Handle edge cases first
        edge_response = handle_edge_cases(request.question, stats)
        if edge_response:
            add_to_conversation(request.session_id, "user", request.question)
            add_to_conversation(request.session_id, "assistant", edge_response)
            log_interaction(
                session_id=request.session_id,
                question=request.question,
                answer=edge_response,
                sources=[],
                retrieval_info={"type": "edge_case"},
            )
            return ChatResponse(
                answer=edge_response,
                sources=[],
                citations=[],
                chunks_used=0,
                session_id=request.session_id,
                timestamp=get_human_readable_timestamp(),
            )

        # Week 3: Get conversation history for memory
        conversation_history = []
        if request.use_memory:
            conversation_history = get_conversation_history(request.session_id, last_n=6)

        if stats["total_chunks"] > 0:
            retrieval_result = retrieve_with_citations(
                query=request.question,
                knowledge_base=kb,
                k=5,
            )

            if retrieval_result["total_used"] > 0:
                # Week 3: Answer with memory context
                result = answer_with_memory(
                    question=request.question,
                    retrieval_result=retrieval_result,
                    conversation_history=conversation_history,
                )
            else:
                logger.info("All chunks below relevance threshold, using fallback")
                result = answer_without_kb(request.question)
                result["answer"] = (
                    "I couldn't find highly relevant information in your documents. "
                    "Here's general guidance:\n\n" + result["answer"]
                )
        else:
            result = answer_without_kb(request.question)

        # Week 3: Save to conversation memory
        add_to_conversation(request.session_id, "user", request.question)
        add_to_conversation(request.session_id, "assistant", result["answer"])

        # Log the interaction
        log_interaction(
            session_id=request.session_id,
            question=request.question,
            answer=result["answer"],
            sources=result.get("sources", []),
            retrieval_info={
                "chunks_used": result.get("chunks_used", 0),
                "citations": result.get("citations", []),
            },
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            citations=result.get("citations", []),
            chunks_used=result.get("chunks_used", 0),
            session_id=request.session_id,
            timestamp=get_human_readable_timestamp(),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Check if the chat service is operational."""
    kb = get_knowledge_base()
    stats = kb.get_stats()
    log_stats = get_stats()
    session_stats = get_session_stats()
    return {
        "status": "ok",
        "knowledge_base_chunks": stats["total_chunks"],
        "knowledge_base_documents": stats["total_documents"],
        "total_interactions_logged": log_stats["total_interactions"],
        "active_sessions": session_stats["total_sessions"],
    }


# ── Week 3: Access Control ───────────────────────────────────────────────────

@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Week 3: Admin login with password verification."""
    if verify_admin(request.password):
        session = create_session(role="admin")
        return AdminLoginResponse(
            success=True,
            message="Admin login successful.",
            session_id=session["session_id"],
        )
    return AdminLoginResponse(
        success=False,
        message="Invalid password.",
    )


@router.post("/session/clear")
async def clear_session_memory(session_id: str = "default"):
    """Week 3: Clear conversation memory for a session."""
    clear_conversation(session_id)
    return {"message": f"Conversation memory cleared for session: {session_id}", "success": True}


@router.get("/sessions")
async def list_sessions():
    """Admin: List all active sessions."""
    sessions = get_all_sessions()
    stats = get_session_stats()
    return {"sessions": sessions, "stats": stats}


# ── Week 2: Admin endpoints ──────────────────────────────────────────────────

@router.get("/history")
async def get_history(session_id: str = None, limit: int = 50):
    """Admin: Get chat history logs."""
    history = get_chat_history(session_id=session_id, limit=limit)
    return {"history": history, "total": len(history)}


@router.get("/history/stats")
async def get_history_stats():
    """Admin: Get chat history statistics."""
    return get_stats()


@router.delete("/history/clear")
async def clear_chat_history():
    """Admin: Clear all chat history logs."""
    clear_history()
    return {"message": "Chat history cleared.", "success": True}


@router.post("/admin/refresh")
async def admin_refresh():
    """Admin: Refresh the knowledge base."""
    try:
        import backend.services.knowledge_base as kb_module
        kb_module._kb_instance = None
        kb = get_knowledge_base()
        stats = kb.get_stats()
        return {
            "message": "Knowledge base refreshed successfully.",
            "success": True,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh failed: {str(e)}"
        )
