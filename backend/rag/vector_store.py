"""
pgvector-backed vector store — replaces ChromaDB.
Uses the DocumentChunk model + cosine distance operator.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import func, text, distinct
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document_chunk import DocumentChunk
from rag.config import DEFAULT_COLLECTION, TOP_K, RELEVANCE_THRESHOLD
from rag.embeddings import embed_texts, embed_query


# ── helpers ────────────────────────────────────────────────────────────

def _session() -> Session:
    return SessionLocal()


# ── public API (same signatures as before) ─────────────────────────────

def list_collections() -> List[str]:
    """Return distinct collection names stored in the DB."""
    db = _session()
    try:
        rows = db.query(distinct(DocumentChunk.collection_name)).all()
        return [r[0] for r in rows if r[0]]
    finally:
        db.close()


def add_documents(
    chunks: List[Dict[str, Any]],
    collection_name: str = DEFAULT_COLLECTION,
) -> int:
    """
    Embed and insert document chunks into Postgres.
    Each chunk dict must have: id, text, metadata.
    """
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    db = _session()
    try:
        for chunk, emb in zip(chunks, embeddings):
            meta = chunk.get("metadata", {})
            obj = DocumentChunk(
                chunk_id=chunk["id"],
                doc_id=meta.get("doc_id", ""),
                doc_title=meta.get("doc_title", ""),
                collection_name=collection_name,
                text=chunk["text"],
                embedding=emb,
                source_path=meta.get("source_path", ""),
                page=meta.get("page"),
                section=meta.get("section", ""),
                content_hash=meta.get("hash", ""),
            )
            db.merge(obj)  # upsert by chunk_id PK
        db.commit()
        return len(chunks)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def query_collection(
    query: str,
    collection_name: str = DEFAULT_COLLECTION,
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Cosine-similarity search within a single collection.
    Returns list of result dicts sorted by relevance (highest first).
    """
    q_emb = embed_query(query)

    db = _session()
    try:
        # pgvector cosine distance: 0 = identical, 2 = opposite
        distance_expr = DocumentChunk.embedding.cosine_distance(q_emb)

        rows = (
            db.query(
                DocumentChunk,
                distance_expr.label("distance"),
            )
            .filter(DocumentChunk.collection_name == collection_name)
            .order_by(distance_expr)
            .limit(top_k)
            .all()
        )

        hits = []
        for chunk, distance in rows:
            score = 1.0 - (distance / 2.0)
            hits.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": {
                    "doc_id": chunk.doc_id,
                    "doc_title": chunk.doc_title,
                    "source_path": chunk.source_path,
                    "page": chunk.page,
                    "section": chunk.section,
                    "chunk_id": chunk.chunk_id,
                },
                "relevance_score": round(score, 4),
            })
        return hits
    finally:
        db.close()


def query_multiple_collections(
    query: str,
    collection_names: List[str],
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Query across multiple collections, merge & dedupe, return top-k.
    """
    all_hits: List[Dict[str, Any]] = []
    seen_ids: set = set()
    for name in collection_names:
        try:
            hits = query_collection(query, name, top_k)
            for h in hits:
                if h["chunk_id"] not in seen_ids:
                    seen_ids.add(h["chunk_id"])
                    h["collection"] = name
                    all_hits.append(h)
        except Exception:
            continue
    all_hits.sort(key=lambda x: x["relevance_score"], reverse=True)
    return all_hits[:top_k]


def filter_by_threshold(
    hits: List[Dict[str, Any]],
    threshold: float = RELEVANCE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Keep only results above the relevance threshold."""
    return [h for h in hits if h["relevance_score"] >= threshold]


def delete_collection(name: str) -> bool:
    """Delete all chunks belonging to a collection."""
    db = _session()
    try:
        deleted = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.collection_name == name)
            .delete()
        )
        db.commit()
        return deleted > 0
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_collection_stats() -> Dict[str, int]:
    """Return chunk count per collection."""
    db = _session()
    try:
        rows = (
            db.query(
                DocumentChunk.collection_name,
                func.count(DocumentChunk.chunk_id),
            )
            .group_by(DocumentChunk.collection_name)
            .all()
        )
        return {name: count for name, count in rows}
    finally:
        db.close()
