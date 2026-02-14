"""
RAG Chatbot API — FastAPI routes for the agentic RAG chatbot.
Endpoints:
  POST /rag/ask        — ask a question
  POST /rag/ingest     — upload & ingest PDFs
  GET  /rag/collections — list collections + stats
  DELETE /rag/collections/{name} — delete a collection
  POST /rag/reset      — reset a session
  GET  /rag/status     — health check
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from pydantic import BaseModel, Field

from rag.config import PDF_UPLOAD_DIR, COLLECTIONS, DEFAULT_COLLECTION
from rag.agent import ask, reset_session
from rag.inference_optimization import get_cache
from rag.ingest import ingest_pdf, ingest_directory
from rag.vector_store import (
    list_collections, get_collection_stats,
    delete_collection, get_or_create_collection,
)
from rag.tools import execute_tool, get_poison_control_contacts
from rag.learning import record_feedback, ingest_learned_interactions, get_learning_stats, log_interaction

router = APIRouter(prefix="/rag", tags=["RAG Chatbot"])


# ── Request / Response Schemas ─────────────────────────────────────────

class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    latitude: Optional[float] = Field(None, description="User latitude for location-based queries")
    longitude: Optional[float] = Field(None, description="User longitude for location-based queries")

class AskResponse(BaseModel):
    answer: str
    why_this_answer: str
    sources: list
    follow_up_questions: list
    safety: dict
    session_id: str
    interaction_id: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    results: list

class CollectionInfo(BaseModel):
    name: str
    count: int

class ToolRequest(BaseModel):
    tool_name: str
    kwargs: dict = {}


# ── /ask ───────────────────────────────────────────────────────────────

@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """
    Ask the RAG chatbot a question.
    Returns a grounded answer with citations, safety assessment, and follow-ups.
    """
    try:
        result = ask(
            query=req.message,
            session_id=req.session_id,
            latitude=req.latitude,
            longitude=req.longitude,
        )
        # Log interaction for the agentic learning loop
        try:
            import json
            conf = result.get("confidence", {})
            iid = log_interaction(
                question=req.message,
                answer=result.get("answer", "")[:2000],
                session_id=result.get("session_id", ""),
                sources=json.dumps(result.get("sources", [])[:3]),
                confidence=conf.get("score", 0.0) if isinstance(conf, dict) else 0.0,
                risk_level=result.get("safety", {}).get("risk_level", "low"),
            )
            result["interaction_id"] = iid
        except Exception:
            result["interaction_id"] = None

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


# ── /ingest ────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdfs(
    files: List[UploadFile] = File(...),
    collection: str = Form(DEFAULT_COLLECTION),
):
    """
    Upload and ingest one or more PDF files into a collection.
    """
    results = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            results.append({"file": file.filename, "error": "Not a PDF file"})
            continue
        # Save to upload directory
        dest = PDF_UPLOAD_DIR / file.filename
        try:
            with open(dest, "wb") as f:
                content = await file.read()
                f.write(content)
            # Ingest
            result = ingest_pdf(str(dest), collection_name=collection)
            results.append(result)
        except Exception as e:
            results.append({"file": file.filename, "error": str(e)})

    return {"status": "completed", "results": results}


# ── /ingest/directory ──────────────────────────────────────────────────

class IngestDirRequest(BaseModel):
    directory: str
    collection: str = DEFAULT_COLLECTION

@router.post("/ingest/directory", response_model=IngestResponse)
async def ingest_from_directory(req: IngestDirRequest):
    """
    Ingest all PDFs from a directory path.
    """
    if not os.path.isdir(req.directory):
        raise HTTPException(status_code=400, detail=f"Directory not found: {req.directory}")
    results = ingest_directory(req.directory, req.collection)
    return {"status": "completed", "results": results}


# ── /collections ───────────────────────────────────────────────────────

@router.get("/collections")
async def get_collections():
    """List all collections with document counts."""
    stats = get_collection_stats()
    collections = [{"name": name, "count": count} for name, count in stats.items()]
    return {
        "collections": collections,
        "available_collections": COLLECTIONS,
        "total_chunks": sum(stats.values()),
    }


@router.delete("/collections/{name}")
async def remove_collection(name: str):
    """Delete a collection and all its data."""
    success = delete_collection(name)
    if success:
        return {"status": "deleted", "collection": name}
    raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")


# ── /reset ─────────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    session_id: str

@router.post("/reset")
async def reset_chat_session(req: ResetRequest):
    """Reset a chat session's history."""
    success = reset_session(req.session_id)
    return {"status": "reset" if success else "no_session_found", "session_id": req.session_id}


# ── /tools ─────────────────────────────────────────────────────────────

@router.post("/tools/execute")
async def execute_safe_tool(req: ToolRequest):
    """Execute a safe tool by name."""
    result = execute_tool(req.tool_name, **req.kwargs)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/tools/contacts/{country}")
async def get_contacts(country: str = "nepal"):
    """Get poison control contacts for a country."""
    return get_poison_control_contacts(country)


# ── /status ────────────────────────────────────────────────────────────

@router.get("/status")
async def rag_status():
    """Health check for the RAG system."""
    stats = get_collection_stats()
    total = sum(stats.values())
    cache = get_cache()
    return {
        "status": "operational",
        "collections": stats,
        "total_chunks": total,
        "total_documents": total,  # frontend uses this field
        "has_data": total > 0,
        "cache_stats": cache.stats,
    }


# ── /feedback — User rates an answer ──────────────────────────────────

class FeedbackRequest(BaseModel):
    interaction_id: str = Field(..., description="The interaction ID returned in the response")
    feedback: str = Field(..., description="'helpful' or 'not_helpful'")
    note: str = Field("", description="Optional note from the user")

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Submit user feedback on a chatbot answer (helpful / not helpful).
    This powers the agentic learning loop — helpful answers get ingested
    back into the knowledge base over time."""
    success = record_feedback(req.interaction_id, req.feedback, req.note)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found or invalid feedback value")
    return {"status": "recorded", "interaction_id": req.interaction_id, "feedback": req.feedback}


# ── /learn — Trigger learning ingestion ────────────────────────────────

@router.post("/learn")
async def trigger_learning():
    """Ingest user-verified (helpful) interactions into the knowledge base.
    This is the agentic learning step — the AI gets smarter from user feedback."""
    try:
        result = ingest_learned_interactions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning error: {str(e)}")


# ── /learning/stats — Learning system metrics ─────────────────────────

@router.get("/learning/stats")
async def learning_stats():
    """Get statistics about the agentic learning system."""
    return get_learning_stats()
