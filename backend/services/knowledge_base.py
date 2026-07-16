"""
Knowledge Base service using ChromaDB for vector storage and retrieval.
Uses free sentence-transformers embeddings (no API key required).
"""
import os
import logging
from typing import List, Tuple
from pathlib import Path

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Collection name in ChromaDB
COLLECTION_NAME = "ngo_knowledge_base"

# Embedding model (free, runs locally)
# all-MiniLM-L6-v2 = 90MB (slower on cloud)
# paraphrase-MiniLM-L3-v2 = 60MB (faster, lighter)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")


def get_embeddings():
    """
    Load sentence-transformers embedding model.
    Downloads automatically on first use (~90MB).
    No API key required.
    """
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


class KnowledgeBase:
    """
    Manages the NGO document knowledge base.
    Handles adding documents, querying, and stats.
    """

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.embeddings = get_embeddings()
        self._vector_store = None
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"KnowledgeBase initialized. Persist dir: {persist_dir}")

    def _get_vector_store(self) -> Chroma:
        """Lazy-load the vector store."""
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
        return self._vector_store

    def add_documents(self, documents: List[Document]) -> int:
        """
        Add chunked documents to the vector store.

        Args:
            documents: List of LangChain Document objects

        Returns:
            Number of chunks added
        """
        if not documents:
            return 0

        vs = self._get_vector_store()
        vs.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to knowledge base")
        return len(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 4
    ) -> List[Tuple[Document, float]]:
        """
        Search for relevant document chunks.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (Document, score) tuples
        """
        vs = self._get_vector_store()
        results = vs.similarity_search_with_relevance_scores(query, k=k)
        logger.info(f"Found {len(results)} relevant chunks for query")
        return results

    def get_retriever(self, k: int = 4):
        """Get a LangChain retriever for use in chains."""
        vs = self._get_vector_store()
        return vs.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def get_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        try:
            # Use the vector store's internal client
            vs = self._get_vector_store()
            collection = vs._collection
            count = collection.count()

            # Get unique source documents
            if count > 0:
                results = collection.get(include=["metadatas"])
                sources = set()
                for meta in results.get("metadatas", []):
                    if meta and "source" in meta:
                        sources.add(meta["source"])
            else:
                sources = set()

            return {
                "total_chunks": count,
                "total_documents": len(sources),
                "collection_name": COLLECTION_NAME,
                "documents": list(sources),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "collection_name": COLLECTION_NAME,
                "documents": [],
            }

    def delete_collection(self):
        """Clear the entire knowledge base (use with caution)."""
        try:
            if self._vector_store:
                self._vector_store._client.delete_collection(COLLECTION_NAME)
                self._vector_store = None
            logger.warning("Knowledge base collection deleted")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


# Singleton instance
_kb_instance = None


def get_knowledge_base() -> KnowledgeBase:
    """Get the singleton KnowledgeBase instance."""
    global _kb_instance
    if _kb_instance is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        _kb_instance = KnowledgeBase(persist_dir=persist_dir)
    return _kb_instance
