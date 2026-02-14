"""
Agentic Learning Module — makes PoisonSense AI smarter over time.

How it works:
1. Every Q&A interaction is logged to SQLite (rag_interactions table)
2. Users can give feedback (helpful / not_helpful) via the API
3. High-quality interactions (helpful + high confidence) are periodically
   ingested into a dedicated ChromaDB collection ("learned_interactions")
4. The agent queries this collection alongside the PDF-based collections,
   so it learns from real user interactions over time

This is a simple but effective agentic feedback loop:
  User asks → Agent answers → User rates → Good answers become training data → Agent improves
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from rag.config import BASE_DIR

# ── Database Setup ─────────────────────────────────────────────────────

_DB_PATH = BASE_DIR / "poisonsense.db"
_LEARNED_COLLECTION = "learned_interactions"


def _get_conn():
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_learning_db():
    """Create the rag_interactions table if it doesn't exist."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rag_interactions (
            id          TEXT PRIMARY KEY,
            session_id  TEXT,
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL,
            sources     TEXT,           -- JSON string of source citations
            confidence  REAL DEFAULT 0,
            risk_level  TEXT DEFAULT 'low',
            feedback    TEXT,           -- 'helpful' | 'not_helpful' | NULL
            feedback_note TEXT,
            ingested    INTEGER DEFAULT 0,   -- 1 = already added to vector store
            created_at  TEXT NOT NULL,
            question_hash TEXT          -- for dedup
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rag_feedback ON rag_interactions(feedback)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rag_ingested ON rag_interactions(ingested)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_rag_hash ON rag_interactions(question_hash)
    """)
    conn.commit()
    conn.close()
    print("✅ RAG learning database ready")


# ── Logging interactions ───────────────────────────────────────────────

def log_interaction(
    question: str,
    answer: str,
    session_id: str = "",
    sources: str = "[]",
    confidence: float = 0.0,
    risk_level: str = "low",
) -> str:
    """Log a Q&A interaction. Returns the interaction ID."""
    interaction_id = str(uuid.uuid4())[:12]
    q_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    try:
        # Skip if we already have this exact question recently (dedup)
        existing = conn.execute(
            "SELECT id FROM rag_interactions WHERE question_hash = ? AND created_at > datetime('now', '-1 hour')",
            (q_hash,)
        ).fetchone()
        if existing:
            conn.close()
            return existing["id"]

        conn.execute(
            """INSERT INTO rag_interactions
               (id, session_id, question, answer, sources, confidence, risk_level, created_at, question_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (interaction_id, session_id, question, answer[:2000], sources, confidence, risk_level, now, q_hash),
        )
        conn.commit()
    finally:
        conn.close()

    return interaction_id


# ── User Feedback ──────────────────────────────────────────────────────

def record_feedback(interaction_id: str, feedback: str, note: str = "") -> bool:
    """Record user feedback on an interaction. feedback = 'helpful' | 'not_helpful'."""
    if feedback not in ("helpful", "not_helpful"):
        return False
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE rag_interactions SET feedback = ?, feedback_note = ? WHERE id = ?",
            (feedback, note, interaction_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ── Learning: Ingest good interactions into vector store ───────────────

def get_learnable_interactions(min_confidence: float = 0.5, limit: int = 50) -> List[Dict]:
    """Get interactions that are eligible for learning (helpful + not yet ingested)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT id, question, answer, confidence, created_at
               FROM rag_interactions
               WHERE feedback = 'helpful'
                 AND ingested = 0
                 AND confidence >= ?
                 AND risk_level = 'low'
               ORDER BY confidence DESC
               LIMIT ?""",
            (min_confidence, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def mark_as_ingested(interaction_ids: List[str]):
    """Mark interactions as ingested into the vector store."""
    if not interaction_ids:
        return
    conn = _get_conn()
    try:
        placeholders = ",".join("?" * len(interaction_ids))
        conn.execute(
            f"UPDATE rag_interactions SET ingested = 1 WHERE id IN ({placeholders})",
            interaction_ids,
        )
        conn.commit()
    finally:
        conn.close()


def ingest_learned_interactions() -> Dict[str, Any]:
    """
    Take all helpful, high-confidence interactions that haven't been ingested yet,
    and add them to the 'learned_interactions' ChromaDB collection.
    
    This is the core of the agentic learning loop.
    """
    from rag.vector_store import add_documents, get_or_create_collection

    interactions = get_learnable_interactions()
    if not interactions:
        return {"status": "no_new_interactions", "count": 0}

    chunks = []
    ids_to_mark = []
    for interaction in interactions:
        # Format as a document chunk that the retriever can use
        doc_text = (
            f"Question: {interaction['question']}\n\n"
            f"Answer: {interaction['answer']}\n\n"
            f"(Verified by user feedback — confidence: {interaction['confidence']:.0%})"
        )
        chunk_id = f"learned_{interaction['id']}"
        chunks.append({
            "id": chunk_id,
            "text": doc_text,
            "metadata": {
                "doc_title": "User-Verified Q&A",
                "doc_id": f"learned_{interaction['id']}",
                "source_path": "user_interaction",
                "page": 0,
                "chunk_id": chunk_id,
                "interaction_id": interaction["id"],
                "learned_at": datetime.now(timezone.utc).isoformat(),
            },
        })
        ids_to_mark.append(interaction["id"])

    # Add to the learned collection
    add_documents(chunks, collection_name=_LEARNED_COLLECTION)
    mark_as_ingested(ids_to_mark)

    return {
        "status": "ingested",
        "count": len(chunks),
        "collection": _LEARNED_COLLECTION,
    }


def get_learning_stats() -> Dict[str, Any]:
    """Get statistics about the learning system."""
    conn = _get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) as c FROM rag_interactions").fetchone()["c"]
        helpful = conn.execute("SELECT COUNT(*) as c FROM rag_interactions WHERE feedback = 'helpful'").fetchone()["c"]
        not_helpful = conn.execute("SELECT COUNT(*) as c FROM rag_interactions WHERE feedback = 'not_helpful'").fetchone()["c"]
        ingested = conn.execute("SELECT COUNT(*) as c FROM rag_interactions WHERE ingested = 1").fetchone()["c"]
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM rag_interactions WHERE feedback = 'helpful' AND ingested = 0"
        ).fetchone()["c"]
        return {
            "total_interactions": total,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "no_feedback": total - helpful - not_helpful,
            "ingested_into_kb": ingested,
            "pending_ingestion": pending,
        }
    finally:
        conn.close()


# Initialize on import
init_learning_db()
