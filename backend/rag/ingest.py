"""
PDF ingestion pipeline.
- Extracts text + page-level metadata from PDFs
- Chunks with heading-aware splitting
- Embeds and stores via pgvector (through vector_store module)
"""

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from rag.config import CHUNK_SIZE, CHUNK_OVERLAP, DEFAULT_COLLECTION
from rag import vector_store


# ── PDF Text Extraction ─────────────────────────────────────────────────

def extract_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text + metadata from every page of a PDF.
    Returns list of {page: int, text: str}.
    Falls back from pdfplumber to PyPDF2.
    """
    pages = []
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                tables = page.extract_tables()
                # Append table text
                for table in tables:
                    for row in table:
                        row_text = " | ".join(str(cell or "") for cell in row)
                        text += "\n" + row_text
                pages.append({"page": i + 1, "text": text.strip()})
    except Exception:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({"page": i + 1, "text": text.strip()})
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {e}")
    return pages


# ── Chunking ────────────────────────────────────────────────────────────

def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Simple sliding-window chunker with sentence-boundary awareness.
    """
    if not text:
        return []

    # Try to split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # If single paragraph exceeds chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = para.replace(". ", ".\n").split("\n")
                current = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current) + len(sent) + 1 <= chunk_size:
                        current = (current + " " + sent).strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
            else:
                current = para

    if current:
        chunks.append(current)

    # Apply overlap by prepending tail of previous chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + " " + chunks[i])
        chunks = overlapped

    return chunks


# ── Ingest a single PDF ────────────────────────────────────────────────

def ingest_pdf(
    pdf_path: str,
    collection_name: str = DEFAULT_COLLECTION,
    doc_title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full pipeline: extract → chunk → embed → store.
    Returns summary dict.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc_id = str(uuid.uuid4())[:8]
    title = doc_title or path.stem
    pages = extract_pages(str(path))
    if not pages:
        raise ValueError("No text extracted from PDF")

    all_chunks = []
    for page_info in pages:
        page_num = page_info["page"]
        page_text = page_info["text"]
        if not page_text:
            continue
        text_chunks = chunk_text(page_text)
        for idx, chunk_text_str in enumerate(text_chunks):
            chunk_id = f"{doc_id}_p{page_num}_c{idx}"
            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text_str,
                "metadata": {
                    "doc_id": doc_id,
                    "doc_title": title,
                    "source_path": str(path.name),
                    "page": page_num,
                    "section": "",
                    "chunk_id": chunk_id,
                    "hash": _compute_hash(chunk_text_str),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "collection": collection_name,
                },
            })

    if not all_chunks:
        raise ValueError("PDF produced no text chunks")

    count = vector_store.add_documents(all_chunks, collection_name)

    return {
        "doc_id": doc_id,
        "doc_title": title,
        "source_path": str(path.name),
        "collection": collection_name,
        "pages_extracted": len(pages),
        "chunks_created": count,
    }


# ── Bulk ingest directory ──────────────────────────────────────────────

def ingest_directory(
    directory: str,
    collection_name: str = DEFAULT_COLLECTION,
) -> List[Dict[str, Any]]:
    """Ingest all PDFs in a directory."""
    results = []
    dir_path = Path(directory)
    for pdf_file in sorted(dir_path.glob("*.pdf")):
        try:
            result = ingest_pdf(str(pdf_file), collection_name)
            results.append(result)
            print(f"  ✅ Ingested: {pdf_file.name} → {result['chunks_created']} chunks")
        except Exception as e:
            results.append({"file": pdf_file.name, "error": str(e)})
            print(f"  ❌ Failed: {pdf_file.name} — {e}")
    return results
