"""
Agentic Learning Module — makes PoisonSense AI smarter over time.

How it works:
1. Every Q&A interaction is logged to Postgres (rag_interactions table)
2. Users can give feedback (helpful / not_helpful) via the API
3. High-quality interactions (helpful + high confidence) are periodically
   ingested into a dedicated pgvector collection ("learned_interactions")
4. The agent queries this collection alongside the PDF-based collections,
   so it learns from real user interactions over time
"""

import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from app.db.session import SessionLocal
from app.models.otp import RAGInteraction

_LEARNED_COLLECTION = "learned_interactions"


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

    db = SessionLocal()
    try:
        # Dedup — skip if same question hash within last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        existing = (
            db.query(RAGInteraction)
            .filter(
                RAGInteraction.question_hash == q_hash,
                RAGInteraction.created_at > one_hour_ago,
            )
            .first()
        )
        if existing:
            return existing.id

        row = RAGInteraction(
            id=interaction_id,
            session_id=session_id,
            question=question,
            answer=answer[:2000],
            sources=sources,
            confidence=confidence,
            risk_level=risk_level,
            question_hash=q_hash,
        )
        db.add(row)
        db.commit()
        return interaction_id
    except Exception:
        db.rollback()
        return interaction_id
    finally:
        db.close()


# ── User Feedback ──────────────────────────────────────────────────────

def record_feedback(interaction_id: str, feedback: str, note: str = "") -> bool:
    """Record user feedback on an interaction."""
    if feedback not in ("helpful", "not_helpful"):
        return False
    db = SessionLocal()
    try:
        row = db.query(RAGInteraction).filter(RAGInteraction.id == interaction_id).first()
        if not row:
            return False
        row.feedback = feedback
        row.feedback_note = note
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


# ── Learning: Ingest good interactions into vector store ───────────────

def get_learnable_interactions(min_confidence: float = 0.5, limit: int = 50) -> List[Dict]:
    """Get interactions eligible for learning (helpful + not yet ingested)."""
    db = SessionLocal()
    try:
        rows = (
            db.query(RAGInteraction)
            .filter(
                RAGInteraction.feedback == "helpful",
                RAGInteraction.ingested == False,
                RAGInteraction.confidence >= min_confidence,
                RAGInteraction.risk_level == "low",
            )
            .order_by(RAGInteraction.confidence.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "confidence": r.confidence,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in rows
        ]
    finally:
        db.close()


def mark_as_ingested(interaction_ids: List[str]):
    """Mark interactions as ingested into the vector store."""
    if not interaction_ids:
        return
    db = SessionLocal()
    try:
        db.query(RAGInteraction).filter(RAGInteraction.id.in_(interaction_ids)).update(
            {RAGInteraction.ingested: True}, synchronize_session=False
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def ingest_learned_interactions() -> Dict[str, Any]:
    """
    Take all helpful, high-confidence, un-ingested interactions and
    add them to the 'learned_interactions' pgvector collection.
    """
    from rag.vector_store import add_documents

    interactions = get_learnable_interactions()
    if not interactions:
        return {"status": "no_new_interactions", "count": 0}

    chunks = []
    ids_to_mark = []
    for interaction in interactions:
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

    add_documents(chunks, collection_name=_LEARNED_COLLECTION)
    mark_as_ingested(ids_to_mark)

    return {
        "status": "ingested",
        "count": len(chunks),
        "collection": _LEARNED_COLLECTION,
    }


def get_learning_stats() -> Dict[str, Any]:
    """Get statistics about the learning system."""
    db = SessionLocal()
    try:
        from sqlalchemy import func

        total = db.query(func.count(RAGInteraction.id)).scalar() or 0
        helpful = (
            db.query(func.count(RAGInteraction.id))
            .filter(RAGInteraction.feedback == "helpful")
            .scalar()
            or 0
        )
        not_helpful = (
            db.query(func.count(RAGInteraction.id))
            .filter(RAGInteraction.feedback == "not_helpful")
            .scalar()
            or 0
        )
        ingested = (
            db.query(func.count(RAGInteraction.id))
            .filter(RAGInteraction.ingested == True)
            .scalar()
            or 0
        )
        pending = (
            db.query(func.count(RAGInteraction.id))
            .filter(RAGInteraction.feedback == "helpful", RAGInteraction.ingested == False)
            .scalar()
            or 0
        )
        return {
            "total_interactions": total,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "no_feedback": total - helpful - not_helpful,
            "ingested_into_kb": ingested,
            "pending_ingestion": pending,
        }
    finally:
        db.close()
