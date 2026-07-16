"""
Week 2: Improved Retrieval Service with citations and relevance scoring.
Provides better context retrieval with source citations at chunk level.
"""
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Minimum relevance score to include a chunk (0.0 - 1.0)
RELEVANCE_THRESHOLD = 0.3


def retrieve_with_citations(
    query: str,
    knowledge_base,
    k: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve relevant chunks with detailed citations.

    Args:
        query: User question
        knowledge_base: KnowledgeBase instance
        k: Number of chunks to retrieve

    Returns:
        dict with 'chunks', 'citations', 'context'
    """
    results = knowledge_base.similarity_search(query, k=k)

    chunks = []
    citations = []

    for doc, score in results:
        # Filter low-relevance chunks
        if score < RELEVANCE_THRESHOLD:
            logger.info(f"Skipping low-relevance chunk (score={score:.2f})")
            continue

        source = doc.metadata.get("source", "Unknown")
        chunk_idx = doc.metadata.get("chunk_index", 0)
        total = doc.metadata.get("total_chunks", 1)

        chunks.append({
            "content": doc.page_content,
            "source": source,
            "chunk_index": chunk_idx,
            "total_chunks": total,
            "relevance_score": round(score, 3),
        })

        # Build citation string
        citation = f"[{source}, chunk {chunk_idx + 1}/{total}, relevance: {score:.0%}]"
        if citation not in citations:
            citations.append(citation)

    # Build context string with inline citations
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source: {chunk['source']}]\n{chunk['content']}"
        )

    context = "\n\n---\n\n".join(context_parts) if context_parts else ""

    # Unique source filenames
    sources = list({c["source"] for c in chunks})

    logger.info(
        f"Retrieved {len(chunks)} chunks from {len(sources)} documents "
        f"(filtered from {len(results)} total)"
    )

    return {
        "chunks": chunks,
        "citations": citations,
        "context": context,
        "sources": sources,
        "total_retrieved": len(results),
        "total_used": len(chunks),
    }


def handle_edge_cases(question: str, kb_stats: dict) -> str | None:
    """
    Handle edge cases before sending to LLM.

    Returns:
        A fallback message string if edge case detected, else None
    """
    question_lower = question.strip().lower()

    # Empty or too short
    if len(question_lower) < 3:
        return "Please ask a complete question about NGO proposals or grant writing."

    # Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "how are you"]
    if question_lower in greetings:
        return (
            "Hello! I'm your NGO Proposal Drafting Assistant. "
            "Ask me anything about grant proposals, budgets, or program design!"
        )

    # Off-topic detection
    off_topic_keywords = [
        "weather", "cricket", "movie", "song", "recipe", "game",
        "stock", "crypto", "bitcoin", "football", "politics"
    ]
    if any(kw in question_lower for kw in off_topic_keywords):
        return (
            "I'm specialized in NGO proposal writing and grant applications. "
            "I can't help with that topic, but feel free to ask about "
            "proposal structure, budgets, or program design!"
        )

    # No documents and question seems document-specific
    if kb_stats.get("total_chunks", 0) == 0:
        doc_specific = ["in the document", "in the file", "uploaded", "according to"]
        if any(phrase in question_lower for phrase in doc_specific):
            return (
                "No documents are uploaded yet. Please upload your NGO documents "
                "in the **Upload Documents** tab first, then ask your question."
            )

    return None  # No edge case — proceed normally
