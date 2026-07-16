"""
NGO Proposal Drafting Bot - FastAPI Backend
Week 3: Conversation memory, access control, proposal generation, final docs.

Run with: uvicorn backend.main:app --reload --port 8000
"""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "True").lower() == "true" else logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

from backend.routes.documents import router as documents_router
from backend.routes.chat import router as chat_router
from backend.routes.proposals import router as proposals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("=" * 50)
    logger.info("NGO Proposal Drafting Bot API starting... (Week 3)")
    logger.info(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'ollama')}")
    logger.info(f"ChromaDB dir: {os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}")

    Path("./data/uploads").mkdir(parents=True, exist_ok=True)
    Path("./data/sample_docs").mkdir(parents=True, exist_ok=True)
    Path(os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")).mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)
    Path("./exports").mkdir(parents=True, exist_ok=True)

    logger.info("API ready. Visit http://localhost:8000/docs")
    logger.info("=" * 50)
    yield
    logger.info("NGO Proposal Drafting Bot API shutting down...")


app = FastAPI(
    title="NGO Proposal Drafting Bot API",
    description="""
    AI-powered tool that helps NGOs draft grant proposals and project documents.

    ## Week 3 Features
    - **Proposal Generator**: Template-based NGO proposal drafting
    - **Conversation Memory**: Context-aware multi-turn chat
    - **Access Control**: Session-based admin authentication
    - **Export**: Download proposals as text files
    - **Chat UX**: Improved interface with history and memory

    ## Student Info
    - **Name**: Yeshwanth Sai R
    - **Reg No**: 411723104059
    - **Project Code**: PRJ-032
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(proposals_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "project": "NGO Proposal Drafting Bot",
        "version": "3.0.0",
        "week": "Week 3",
        "student": "Yeshwanth Sai R",
        "reg_no": "411723104059",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "message": "NGO Proposal Drafting Bot API is running (Week 3)",
    }
