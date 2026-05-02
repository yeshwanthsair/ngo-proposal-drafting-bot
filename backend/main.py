"""
NGO Proposal Drafting Bot - FastAPI Backend
Entry point for the API server.

Run with: uvicorn backend.main:app --reload --port 8000
"""
import os
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "True").lower() == "true" else logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Import routers
from backend.routes.documents import router as documents_router
from backend.routes.chat import router as chat_router

# Create FastAPI app
app = FastAPI(
    title="NGO Proposal Drafting Bot API",
    description="""
    AI-powered tool that helps NGOs draft grant proposals and project documents.
    
    ## Features (Week 1)
    - **Document Upload**: Upload PDF, TXT, DOCX files to the knowledge base
    - **Knowledge Base**: ChromaDB vector store with semantic search
    - **Chat/Q&A**: Ask questions grounded in uploaded documents
    
    ## Student Info
    - **Name**: Yeshwanth Sai R
    - **Reg No**: 411723104059
    - **Project Code**: PRJ-032
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allows Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info."""
    return {
        "project": "NGO Proposal Drafting Bot",
        "version": "1.0.0",
        "student": "Yeshwanth Sai R",
        "reg_no": "411723104059",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "NGO Proposal Drafting Bot API is running",
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 50)
    logger.info("NGO Proposal Drafting Bot API starting...")
    logger.info(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'gemini')}")
    logger.info(f"ChromaDB dir: {os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}")

    # Ensure required directories exist
    Path("./data/uploads").mkdir(parents=True, exist_ok=True)
    Path("./data/sample_docs").mkdir(parents=True, exist_ok=True)
    Path(os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")).mkdir(parents=True, exist_ok=True)

    logger.info("API ready. Visit http://localhost:8000/docs")
    logger.info("=" * 50)
