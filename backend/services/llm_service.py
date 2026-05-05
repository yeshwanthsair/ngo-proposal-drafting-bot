"""
LLM service - supports both Groq (API) and Ollama (local).
Set LLM_PROVIDER in .env to switch between them.
"""
import os
import time
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
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Get free key at https://console.groq.com"
            )
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        logger.info(f"Using Groq: {model}")
        return ChatGroq(api_key=api_key, model_name=model, temperature=0.3)

    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ValueError("Run: pip install langchain-ollama")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info(f"Using Ollama: {model}")
        return ChatOllama(model=model, base_url=base_url, temperature=0.3)

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'ollama'.")


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def answer_question(question: str, retriever) -> dict:
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
        sources = list({doc.metadata.get("source", "Unknown") for doc in source_docs})
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


def answer_without_kb(question: str) -> dict:
    try:
        llm = get_llm()
        prompt = (
            "You are an expert NGO proposal writing assistant.\n"
            "Answer based on your general knowledge about NGO proposals.\n\n"
            f"Question: {question}\n\nAnswer:"
        )
        response = llm.invoke(prompt)
        return {
            "answer": response.content,
            "sources": ["General Knowledge (no documents in knowledge base)"],
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
