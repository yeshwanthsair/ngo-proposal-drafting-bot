"""
Week 3: Improved LLM service with conversation memory support.
Supports Ollama (local) and Groq (API).
"""
import os
import logging
from typing import List, Dict

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

# NGO-specific prompt with citation instructions
NGO_PROMPT_WITH_CITATIONS = """You are an expert NGO proposal writing assistant.

IMPORTANT: You have been provided with content from the user's uploaded documents below. You MUST use this content to answer the question. Do NOT say there are no uploaded documents.

Context from uploaded documents:
{context}

Question: {question}

Instructions:
- If the context above contains relevant information, summarize or answer from it directly
- Always refer to the context as "the uploaded document" or "based on the document"
- Be specific, practical, and professional

Answer:"""


NGO_PROMPT_WITH_MEMORY = """You are an expert NGO proposal writing assistant.

IMPORTANT: You have been provided with content from the user's uploaded documents below. You MUST use this content to answer the question. Do NOT say there are no uploaded documents.

Conversation History:
{history}

Context from uploaded documents:
{context}

Current Question: {question}

Instructions:
- If the context above contains relevant information, use it directly to answer
- Always refer to the context as "the uploaded document"
- Use conversation history only for follow-up context, not to override document content

Answer:"""


# Fallback prompt when no documents are uploaded
NGO_FALLBACK_PROMPT = """You are an expert NGO proposal writing assistant with 15+ years of experience 
in grant writing, program design, and donor relations.

Provide expert guidance on the following question. Be specific, practical, and professional.
Use real-world NGO examples where helpful.

Question: {question}

Expert Answer:"""


def get_llm():
    """
    Initialize LLM. Supports Groq (cloud) and Ollama (local).
    - On Streamlit Cloud: set LLM_PROVIDER=groq and GROQ_API_KEY in secrets
    - Locally: set LLM_PROVIDER=ollama (default)
    """
    # If GROQ_API_KEY is set, always use Groq (works on Streamlit Cloud)
    groq_api_key = os.getenv("GROQ_API_KEY")
    provider = os.getenv("LLM_PROVIDER", "groq" if groq_api_key else "ollama").lower()

    if provider == "groq":
        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Get a free key at https://console.groq.com "
                "and add it to Streamlit Cloud Secrets: GROQ_API_KEY = 'your_key'"
            )
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        logger.info(f"Using Groq: {model}")
        return ChatGroq(api_key=groq_api_key, model_name=model, temperature=0.3)

    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ValueError("Run: pip install langchain-ollama")
        model = os.getenv("OLLAMA_MODEL", "tinyllama")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info(f"Using Ollama: {model}")
        return ChatOllama(model=model, base_url=base_url, temperature=0.3)

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'ollama'.")


def format_docs(docs: List[Document]) -> str:
    """Combine retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def answer_question(question: str, retrieval_result: dict) -> dict:
    """
    Week 2: Answer with improved prompt and citation support.

    Args:
        question: User question
        retrieval_result: Result from retrieve_with_citations()

    Returns:
        dict with 'answer', 'sources', 'citations'
    """
    try:
        llm = get_llm()
        context = retrieval_result.get("context", "")
        sources = retrieval_result.get("sources", [])
        citations = retrieval_result.get("citations", [])

        prompt = PromptTemplate(
            template=NGO_PROMPT_WITH_CITATIONS,
            input_variables=["context", "question"],
        )

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
            "chunks_used": retrieval_result.get("total_used", 0),
        }

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise


def answer_without_kb(question: str) -> dict:
    """
    Week 2: Improved fallback answer when no documents uploaded.
    Uses better prompt for general NGO guidance.
    """
    try:
        llm = get_llm()

        prompt = PromptTemplate(
            template=NGO_FALLBACK_PROMPT,
            input_variables=["question"],
        )

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"question": question})

        return {
            "answer": answer,
            "sources": [],
            "citations": [],
            "chunks_used": 0,
        }

    except Exception as e:
        logger.error(f"Error in fallback answer: {e}")
        raise


def answer_with_memory(
    question: str,
    retrieval_result: dict,
    conversation_history: List[Dict],
) -> dict:
    """
    Week 3: Answer using conversation memory + knowledge base context.

    Args:
        question: Current user question
        retrieval_result: Result from retrieve_with_citations()
        conversation_history: List of previous messages [{role, content}]

    Returns:
        dict with 'answer', 'sources', 'citations', 'chunks_used'
    """
    try:
        llm = get_llm()
        context = retrieval_result.get("context", "")
        sources = retrieval_result.get("sources", [])
        citations = retrieval_result.get("citations", [])

        # Format conversation history
        if conversation_history:
            history_lines = []
            for msg in conversation_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_lines.append(f"{role}: {msg['content'][:300]}")
            history_text = "\n".join(history_lines)
        else:
            history_text = "No previous conversation."

        prompt = PromptTemplate(
            template=NGO_PROMPT_WITH_MEMORY,
            input_variables=["history", "context", "question"],
        )

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({
            "history": history_text,
            "context": context,
            "question": question,
        })

        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
            "chunks_used": retrieval_result.get("total_used", 0),
        }

    except Exception as e:
        logger.error(f"Error in answer_with_memory: {e}")
        # Fallback to regular answer
        return answer_question(question, retrieval_result)
