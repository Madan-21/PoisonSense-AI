"""
ChromaDB vector store wrapper — collection-aware.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional

from rag.config import CHROMA_PERSIST_DIR, DEFAULT_COLLECTION, COLLECTIONS, TOP_K, RELEVANCE_THRESHOLD
from rag.embeddings import EmbeddingFunction

_client: Optional[chromadb.ClientAPI] = None
_ef = EmbeddingFunction()


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        print(f"✅ ChromaDB initialized at {CHROMA_PERSIST_DIR}")
    return _client


def get_or_create_collection(name: str = DEFAULT_COLLECTION):
    client = _get_client()
    return client.get_or_create_collection(
        name=name,
        embedding_function=_ef,
        metadata={"hnsw:space": "cosine"},
    )


def list_collections() -> List[str]:
    client = _get_client()
    return [c.name for c in client.list_collections()]


def add_documents(
    chunks: List[Dict[str, Any]],
    collection_name: str = DEFAULT_COLLECTION,
):
    """
    Add document chunks to a collection.
    Each chunk dict must have: id, text, metadata
    """
    coll = get_or_create_collection(collection_name)
    ids = [c["id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metas = [c["metadata"] for c in chunks]
    # ChromaDB handles batching internally
    batch = 100
    for i in range(0, len(ids), batch):
        coll.add(
            ids=ids[i : i + batch],
            documents=docs[i : i + batch],
            metadatas=metas[i : i + batch],
        )
    return len(ids)


def query_collection(
    query: str,
    collection_name: str = DEFAULT_COLLECTION,
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Query a single collection. Returns list of results sorted by relevance.
    """
    coll = get_or_create_collection(collection_name)
    if coll.count() == 0:
        return []
    results = coll.query(
        query_texts=[query],
        n_results=min(top_k, coll.count()),
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for idx in range(len(results["ids"][0])):
        distance = results["distances"][0][idx]
        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Convert to similarity score (1 = identical, 0 = orthogonal)
        score = 1.0 - (distance / 2.0)
        hits.append({
            "chunk_id": results["ids"][0][idx],
            "text": results["documents"][0][idx],
            "metadata": results["metadatas"][0][idx],
            "relevance_score": round(score, 4),
        })
    return hits


def query_multiple_collections(
    query: str,
    collection_names: List[str],
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Query multiple collections, merge & dedupe, return top-k by score.
    """
    all_hits = []
    seen_ids = set()
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


def delete_collection(name: str):
    client = _get_client()
    try:
        client.delete_collection(name)
        return True
    except Exception:
        return False


def get_collection_stats() -> Dict[str, int]:
    """Return count per collection."""
    client = _get_client()
    stats = {}
    for c in client.list_collections():
        stats[c.name] = c.count()
    return stats
