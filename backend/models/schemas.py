"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request body for chat/Q&A endpoint."""
    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    session_id: Optional[str] = Field(default="default", description="Session identifier")


class ChatResponse(BaseModel):
    """Response from chat/Q&A endpoint."""
    answer: str
    sources: List[str] = []
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


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
