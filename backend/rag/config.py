"""
RAG Configuration — single source of truth for all tuneable knobs.
Environment variables override defaults (loaded via python-dotenv).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Fallback secrets (so the app works even if .env is deleted) ─────
_GROQ_KEY_FALLBACK = "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"

# ── Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
PDF_UPLOAD_DIR = BASE_DIR / "rag" / "pdf_uploads"
CHROMA_PERSIST_DIR = BASE_DIR / "rag" / "chroma_store"
PDF_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# ── Embedding ───────────────────────────────────────────────────────────
# "openai" | "local"  (local = sentence-transformers/all-MiniLM-L6-v2)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
LOCAL_EMBEDDING_MODEL = os.getenv(
    "LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ── LLM ─────────────────────────────────────────────────────────────────
# "groq" | "openai" | "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
_raw_groq_key = os.getenv("GROQ_API_KEY", "")
GROQ_API_KEY = _raw_groq_key if (_raw_groq_key and not _raw_groq_key.startswith("your-")) else _GROQ_KEY_FALLBACK
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Chunking ────────────────────────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# ── Retrieval ───────────────────────────────────────────────────────────
TOP_K = int(os.getenv("TOP_K", "8"))
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.25"))

# ── Collections (default set) ──────────────────────────────────────────
DEFAULT_COLLECTION = "general"
COLLECTIONS = [
    "general",
    "prevention_storage",
    "symptom_recognition",
    "first_aid",
    "emergency_escalation",
    "regional_resources",
]
