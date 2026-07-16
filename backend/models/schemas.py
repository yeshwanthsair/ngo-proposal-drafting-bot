"""
Pydantic schemas for request/response validation.
Week 3: Added session memory, access control fields.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from backend.utils.datetime_utils import get_human_readable_timestamp


class ChatRequest(BaseModel):
    """Request body for chat/Q&A endpoint."""
    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    session_id: Optional[str] = Field(default="default", description="Session identifier")
    use_memory: Optional[bool] = Field(default=True, description="Week 3: Use conversation memory")


class ChatResponse(BaseModel):
    """Response from chat/Q&A endpoint."""
    answer: str
    sources: List[str] = []
    citations: List[str] = []
    chunks_used: int = 0
    session_id: str
    timestamp: str = Field(default_factory=get_human_readable_timestamp)


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""
    filename: str
    chunks_created: int
    message: str
    success: bool


class DocumentListResponse(BaseModel):
    """List of documents in the knowledge base."""
    documents: List[str]
    total: int


class KnowledgeBaseStatsResponse(BaseModel):
    """Stats about the current knowledge base."""
    total_documents: int
    total_chunks: int
    collection_name: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


# ── Week 3: Access Control ───────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    """Admin login request."""
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response."""
    success: bool
    message: str
    session_id: Optional[str] = None
