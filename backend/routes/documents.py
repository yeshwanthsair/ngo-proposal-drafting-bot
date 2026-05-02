"""
Document management routes.
Handles file upload, parsing, and knowledge base population.
"""
import os
import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.models.schemas import DocumentUploadResponse, DocumentListResponse, KnowledgeBaseStatsResponse
from backend.services.document_parser import parse_and_chunk
from backend.services.knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])

# Temp upload directory
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc"}
MAX_FILE_SIZE_MB = 10


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base.
    Supported formats: PDF, TXT, DOCX

    The document is parsed, chunked, and stored in ChromaDB for retrieval.
    """
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not supported. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    # Save uploaded file temporarily
    temp_path = UPLOAD_DIR / file.filename
    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()

            # Check file size
            size_mb = len(content) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large ({size_mb:.1f}MB). Max allowed: {MAX_FILE_SIZE_MB}MB"
                )

            buffer.write(content)

        logger.info(f"Saved uploaded file: {file.filename} ({size_mb:.2f}MB)")

        # Parse and chunk the document
        documents = parse_and_chunk(str(temp_path))

        # Add to knowledge base
        kb = get_knowledge_base()
        chunks_added = kb.add_documents(documents)

        return DocumentUploadResponse(
            filename=file.filename,
            chunks_created=chunks_added,
            message=f"Successfully processed '{file.filename}' into {chunks_added} searchable chunks.",
            success=True,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """List all documents currently in the knowledge base."""
    kb = get_knowledge_base()
    stats = kb.get_stats()
    return DocumentListResponse(
        documents=stats["documents"],
        total=stats["total_documents"],
    )


@router.get("/stats", response_model=KnowledgeBaseStatsResponse)
async def get_stats():
    """Get statistics about the knowledge base."""
    kb = get_knowledge_base()
    stats = kb.get_stats()
    return KnowledgeBaseStatsResponse(
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
        collection_name=stats["collection_name"],
    )


@router.delete("/delete/{filename}")
async def delete_document(filename: str):
    """
    Delete a specific document from the knowledge base.
    Removes all chunks associated with that document.
    """
    try:
        kb = get_knowledge_base()
        vs = kb._get_vector_store()
        collection = vs._collection
        
        # Get all items with this source filename
        results = collection.get(
            where={"source": filename},
            include=["metadatas"]
        )
        
        if not results["ids"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{filename}' not found in knowledge base"
            )
        
        # Delete all chunks from this document
        collection.delete(ids=results["ids"])
        
        logger.info(f"Deleted {len(results['ids'])} chunks from document '{filename}'")
        
        return {
            "message": f"Successfully deleted '{filename}' ({len(results['ids'])} chunks removed)",
            "success": True,
            "chunks_deleted": len(results["ids"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.delete("/clear")
async def clear_knowledge_base():
    """
    Clear all documents from the knowledge base.
    WARNING: This is irreversible.
    """
    kb = get_knowledge_base()
    kb.delete_collection()
    return {"message": "Knowledge base cleared successfully.", "success": True}


@router.post("/clear")
async def clear_knowledge_base_post():
    """
    Clear all documents from the knowledge base (POST method for Streamlit).
    WARNING: This is irreversible.
    """
    kb = get_knowledge_base()
    kb.delete_collection()
    return {"message": "Knowledge base cleared successfully.", "success": True}
