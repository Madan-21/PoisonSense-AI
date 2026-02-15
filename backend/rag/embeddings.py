"""
Embedding layer — Hugging Face Inference API (free with HF token, Vercel-safe).
Uses the sentence-transformers/all-MiniLM-L6-v2 model (384 dimensions).

NOTE: As of 2025, HF migrated from api-inference.huggingface.co to
router.huggingface.co. A free HF_API_TOKEN is now required.
"""

from typing import List
import requests
from rag.config import HF_API_TOKEN, EMBEDDING_MODEL

# New HF Inference API endpoint (old api-inference.huggingface.co is 410 Gone)
_HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{EMBEDDING_MODEL}/pipeline/feature-extraction"


def _headers() -> dict:
    h = {}
    if HF_API_TOKEN:
        h["Authorization"] = f"Bearer {HF_API_TOKEN}"
    return h


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of strings via Hugging Face Inference API."""
    if not texts:
        return []
    all_embeddings: List[List[float]] = []
    batch_size = 64  # HF Inference API handles batches well
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = requests.post(
            _HF_API_URL,
            headers=_headers(),
            json={"inputs": batch, "options": {"wait_for_model": True}},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # HF returns a nested list: each item is a list of token embeddings
        # For sentence-transformers models, it returns the pooled embedding directly
        for item in data:
            if isinstance(item[0], list):
                # Token-level embeddings — mean pool to get sentence embedding (pure Python, no numpy)
                num_tokens = len(item)
                dim = len(item[0])
                pooled = [sum(item[t][d] for t in range(num_tokens)) / num_tokens for d in range(dim)]
                all_embeddings.append(pooled)
            else:
                # Already a sentence embedding
                all_embeddings.append(item)
    return all_embeddings


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
