"""
Week 2: Chat History Logger.
Logs all Q&A interactions to a JSON file for review and analysis.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from backend.utils.datetime_utils import get_human_readable_timestamp

logger = logging.getLogger(__name__)

LOG_DIR = Path("./logs")
LOG_FILE = LOG_DIR / "chat_history.json"


def ensure_log_dir():
    """Create logs directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("[]")


def log_interaction(
    session_id: str,
    question: str,
    answer: str,
    sources: List[str],
    retrieval_info: Dict[str, Any] = None,
):
    """
    Log a Q&A interaction to the chat history file.

    Args:
        session_id: Session identifier
        question: User question
        answer: Bot answer
        sources: Source documents used
        retrieval_info: Optional retrieval metadata
    """
    ensure_log_dir()

    entry = {
        "timestamp": get_human_readable_timestamp(),
        "iso_timestamp": datetime.now().isoformat(),  # Keep ISO for sorting
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieval_info": retrieval_info or {},
    }

    try:
        # Read existing logs
        existing = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        existing.append(entry)

        # Keep only last 500 entries
        if len(existing) > 500:
            existing = existing[-500:]

        LOG_FILE.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.info(f"Logged interaction for session: {session_id}")

    except Exception as e:
        logger.error(f"Failed to log interaction: {e}")


def get_chat_history(session_id: str = None, limit: int = 50) -> List[Dict]:
    """
    Retrieve chat history.

    Args:
        session_id: Filter by session (None = all sessions)
        limit: Max number of entries to return

    Returns:
        List of interaction dicts
    """
    ensure_log_dir()

    try:
        all_logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))

        if session_id:
            all_logs = [l for l in all_logs if l.get("session_id") == session_id]

        # Return most recent first
        return list(reversed(all_logs[-limit:]))

    except Exception as e:
        logger.error(f"Failed to read chat history: {e}")
        return []


def get_stats() -> Dict[str, Any]:
    """Get chat history statistics."""
    ensure_log_dir()

    try:
        all_logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        sessions = set(l.get("session_id") for l in all_logs)

        return {
            "total_interactions": len(all_logs),
            "total_sessions": len(sessions),
            "log_file": str(LOG_FILE),
        }
    except Exception:
        return {"total_interactions": 0, "total_sessions": 0}


def clear_history():
    """Clear all chat history."""
    ensure_log_dir()
    LOG_FILE.write_text("[]")
    logger.info("Chat history cleared")
