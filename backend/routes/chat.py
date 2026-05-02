"""
Chat/Q&A routes.
Handles question answering using the knowledge base.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.knowledge_base import get_knowledge_base
from backend.services.llm_service import answer_question, answer_without_kb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question about NGO proposals and grant writing.

    If documents are uploaded, answers are grounded in the knowledge base.
    Otherwise, falls back to general LLM knowledge.
    """
    logger.info(f"Question received: {request.question[:80]}...")

    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()

        if stats["total_chunks"] > 0:
            # Use knowledge base for grounded answers
            retriever = kb.get_retriever(k=4)
            result = answer_question(request.question, retriever)
        else:
            # Fallback: no documents uploaded yet
            logger.info("No documents in KB, using fallback LLM answer")
            result = answer_without_kb(request.question)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
        )

    except ValueError as e:
        # LLM config errors (missing API key, etc.)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
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
    return {
        "status": "ok",
        "knowledge_base_chunks": stats["total_chunks"],
        "knowledge_base_documents": stats["total_documents"],
    }
