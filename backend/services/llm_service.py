"""
LLM service using Ollama (runs locally, 100% free, no API keys).
Install Ollama from: https://ollama.com/download
Then run: ollama pull llama3.2
"""
import os
import logging
from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

NGO_SYSTEM_PROMPT = """You are an expert NGO proposal writing assistant with deep knowledge of:
- Grant writing and proposal structure
- NGO program design and implementation
- Donor requirements and reporting standards
- Social impact measurement

Use the provided context from NGO documents to answer questions accurately.
If the context does not contain enough information, say so clearly and provide general guidance.
Always be helpful, professional, and focused on NGO/grant writing topics.

Context from knowledge base:
{context}

Question: {question}

Answer:"""


def get_llm():
    """
    Initialize Ollama LLM (runs locally, no API key needed).
    
    Setup:
    1. Download Ollama: https://ollama.com/download
    2. Run: ollama pull llama3.2
    3. That's it!
    """
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        raise ValueError(
            "langchain-ollama not installed. Run: pip install langchain-ollama"
        )
    
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    logger.info(f"Using Ollama model: {model} at {base_url}")
    
    try:
        llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=0.3,
        )
        # Test connection
        llm.invoke("Hi")
        return llm
    except Exception as e:
        raise ValueError(
            f"Cannot connect to Ollama at {base_url}. "
            f"Error: {e}\n\n"
            "Setup instructions:\n"
            "1. Download Ollama from https://ollama.com/download\n"
            "2. Install and start Ollama\n"
            f"3. Run: ollama pull {model}\n"
            "4. Restart this backend"
        )


def format_docs(docs: List[Document]) -> str:
    """Combine retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def answer_question(question: str, retriever) -> dict:
    """Answer a question using the knowledge base."""
    try:
        llm = get_llm()
        prompt = PromptTemplate(
            template=NGO_SYSTEM_PROMPT,
            input_variables=["context", "question"],
        )

        source_docs = retriever.invoke(question)
        context = format_docs(source_docs)

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        sources = list({
            doc.metadata.get("source", "Unknown")
            for doc in source_docs
        })

        return {"answer": answer, "sources": sources}

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise


def answer_without_kb(question: str) -> dict:
    """Answer using only the LLM (fallback when no documents uploaded)."""
    try:
        llm = get_llm()
        fallback_prompt = (
            "You are an expert NGO proposal writing assistant.\n"
            "The knowledge base is currently empty (no documents uploaded yet).\n"
            "Please answer based on your general knowledge about NGO proposals and grant writing.\n\n"
            f"Question: {question}\n\nAnswer:"
        )
        response = llm.invoke(fallback_prompt)
        return {
            "answer": response.content,
            "sources": ["General Knowledge (no documents in knowledge base)"],
        }
    except Exception as e:
        logger.error(f"Error in fallback answer: {e}")
        raise
