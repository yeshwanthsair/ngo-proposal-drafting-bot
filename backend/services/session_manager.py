"""
Week 3: Session Manager for access control and conversation memory.
Handles user sessions, conversation history, and basic access control.
"""
import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Session storage (in-memory for simplicity)
_sessions: Dict[str, dict] = {}

# Admin password from env (loaded dynamically to support testing)
def get_admin_password():
    """Get admin password from environment."""
    return os.getenv("ADMIN_PASSWORD", "admin123")

# Session expiry (hours)
SESSION_EXPIRY_HOURS = 24


def create_session(session_id: str = None, role: str = "user") -> dict:
    """Create a new session."""
    if not session_id:
        session_id = secrets.token_hex(16)

    session = {
        "session_id": session_id,
        "role": role,  # "user" or "admin"
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "conversation_history": [],  # Week 3: conversation memory
        "message_count": 0,
    }
    _sessions[session_id] = session
    logger.info(f"Created session: {session_id} (role={role})")
    return session


def get_session(session_id: str) -> Optional[dict]:
    """Get an existing session or create a new one."""
    if session_id not in _sessions:
        return create_session(session_id=session_id)

    session = _sessions[session_id]
    # Update last active
    session["last_active"] = datetime.now().isoformat()
    return session


def verify_admin(password: str) -> bool:
    """Verify admin password."""
    return password == get_admin_password()


def add_to_conversation(session_id: str, role: str, content: str):
    """
    Add a message to the conversation history for memory.

    Args:
        session_id: Session identifier
        role: 'user' or 'assistant'
        content: Message content
    """
    session = get_session(session_id)
    if session is None:
        session = create_session(session_id)

    session["conversation_history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    })
    session["message_count"] += 1

    # Keep only last 20 messages to avoid context overflow
    if len(session["conversation_history"]) > 20:
        session["conversation_history"] = session["conversation_history"][-20:]


def get_conversation_history(session_id: str, last_n: int = 6) -> List[dict]:
    """
    Get recent conversation history for context.

    Args:
        session_id: Session identifier
        last_n: Number of recent messages to return

    Returns:
        List of message dicts with role and content
    """
    session = get_session(session_id)
    if not session:
        return []
    history = session.get("conversation_history", [])
    return history[-last_n:] if len(history) > last_n else history


def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    session = get_session(session_id)
    if session:
        session["conversation_history"] = []
        session["message_count"] = 0
        logger.info(f"Cleared conversation for session: {session_id}")


def get_all_sessions() -> List[dict]:
    """Get all active sessions (admin only)."""
    return [
        {
            "session_id": s["session_id"],
            "role": s["role"],
            "created_at": s["created_at"],
            "last_active": s["last_active"],
            "message_count": s["message_count"],
        }
        for s in _sessions.values()
    ]


def get_session_stats() -> dict:
    """Get session statistics."""
    total = len(_sessions)
    admin_sessions = sum(1 for s in _sessions.values() if s.get("role") == "admin")
    user_sessions = total - admin_sessions
    total_messages = sum(s.get("message_count", 0) for s in _sessions.values())

    return {
        "total_sessions": total,
        "admin_sessions": admin_sessions,
        "user_sessions": user_sessions,
        "total_messages": total_messages,
    }
