"""
Script to load sample NGO documents into the knowledge base.
Run this after starting the FastAPI server.

Usage: python scripts/load_sample_docs.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from backend.services.document_parser import parse_and_chunk
from backend.services.knowledge_base import get_knowledge_base


def load_sample_documents():
    sample_dir = Path("./data/sample_docs")

    if not sample_dir.exists():
        print("❌ data/sample_docs directory not found.")
        return

    files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))

    if not files:
        print("❌ No sample documents found in data/sample_docs/")
        return

    kb = get_knowledge_base()
    print(f"📚 Loading {len(files)} sample document(s) into knowledge base...\n")

    total_chunks = 0
    for file_path in files:
        try:
            docs = parse_and_chunk(str(file_path))
            kb.add_documents(docs)
            total_chunks += len(docs)
            print(f"  ✅ {file_path.name} → {len(docs)} chunks")
        except Exception as e:
            print(f"  ❌ {file_path.name} → Error: {e}")

    print(f"\n✅ Done! Total chunks in knowledge base: {total_chunks}")

    stats = kb.get_stats()
    print(f"📊 Knowledge Base Stats:")
    print(f"   Documents: {stats['total_documents']}")
    print(f"   Chunks:    {stats['total_chunks']}")


if __name__ == "__main__":
    load_sample_documents()
