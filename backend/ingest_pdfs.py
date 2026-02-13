"""
Quick script to ingest all PDFs from the Pdf's directory into the RAG system.
Run from the backend/ directory:
    python ingest_pdfs.py
"""

import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.ingest import ingest_pdf, ingest_directory
from rag.vector_store import get_collection_stats

# ── PDF directories to ingest ────────────────────────────────────────
PDF_DIRS = [
    # The user's toxicology PDFs (workspace sibling folder)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Pdf's"),
    # The user's toxicology PDFs (alternate path)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Pdf's"),
    # Any PDFs in the upload directory
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag", "pdf_uploads"),
]

COLLECTION = "general"  # Change to route to specific collections


def main():
    print("=" * 60)
    print("PoisonSense RAG — PDF Ingestion")
    print("=" * 60)

    total_chunks = 0
    total_docs = 0

    for pdf_dir in PDF_DIRS:
        abs_dir = os.path.abspath(pdf_dir)
        if not os.path.isdir(abs_dir):
            print(f"\n⚠️  Directory not found: {abs_dir}")
            continue

        pdf_files = [f for f in os.listdir(abs_dir) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"\n📂 No PDFs found in: {abs_dir}")
            continue

        print(f"\n📂 Ingesting from: {abs_dir}")
        print(f"   Found {len(pdf_files)} PDF(s)")

        for pdf_file in sorted(pdf_files):
            pdf_path = os.path.join(abs_dir, pdf_file)
            try:
                result = ingest_pdf(pdf_path, collection_name=COLLECTION)
                total_chunks += result["chunks_created"]
                total_docs += 1
                print(f"   ✅ {pdf_file}")
                print(f"      → {result['pages_extracted']} pages, {result['chunks_created']} chunks")
            except Exception as e:
                print(f"   ❌ {pdf_file}: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Summary: {total_docs} documents, {total_chunks} total chunks")
    print("\n📊 Collection stats:")
    for name, count in get_collection_stats().items():
        print(f"   • {name}: {count} chunks")
    print("=" * 60)


if __name__ == "__main__":
    main()
