"""
RAG Configuration — reads from app.core.config.settings.
Fully free stack: Groq (LLM) + Hugging Face Inference API (embeddings).
No local file paths. No hardcoded API keys.
"""

from app.core.config import settings

# ── Embedding (Hugging Face Inference API — free, no local model) ──────
HF_API_TOKEN = settings.HF_API_TOKEN or ""
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
EMBEDDING_DIMENSIONS = settings.EMBEDDING_DIMENSIONS

# ── LLM (Groq — free) ────────────────────────────────────────────────
LLM_PROVIDER = settings.LLM_PROVIDER
GROQ_API_KEY = settings.GROQ_API_KEY or ""
GROQ_MODEL = settings.GROQ_MODEL

# ── Chunking ──────────────────────────────────────────────────────────
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

# ── Retrieval ─────────────────────────────────────────────────────────
TOP_K = settings.TOP_K
RELEVANCE_THRESHOLD = settings.RELEVANCE_THRESHOLD

# ── Collections ───────────────────────────────────────────────────────
DEFAULT_COLLECTION = "general"
COLLECTIONS = [
    "general",
    "prevention_storage",
    "symptom_recognition",
    "first_aid",
    "emergency_escalation",
    "regional_resources",
]
