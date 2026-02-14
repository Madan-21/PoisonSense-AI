"""
Pluggable embedding layer.
Supports: sentence-transformers (local) or OpenAI.
"""

from typing import List
from rag.config import (
    EMBEDDING_PROVIDER, LOCAL_EMBEDDING_MODEL,
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL,
)

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(LOCAL_EMBEDDING_MODEL)
        print(f"✅ Loaded local embedding model: {LOCAL_EMBEDDING_MODEL}")
    return _local_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of strings."""
    if EMBEDDING_PROVIDER == "openai":
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resp = client.embeddings.create(input=texts, model=OPENAI_EMBEDDING_MODEL)
        return [d.embedding for d in resp.data]
    else:
        model = _get_local_model()
        # Process in small batches to limit peak memory on free-tier hosts
        batch_size = 32
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embs = model.encode(batch, show_progress_bar=False).tolist()
            all_embeddings.extend(embs)
        return all_embeddings


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]


class EmbeddingFunction:
    """ChromaDB-compatible embedding function wrapper."""

    def __init__(self):
        pass

    def __call__(self, input: List[str]) -> List[List[float]]:
        return embed_texts(input)

    def embed_query(self, input: List[str]) -> List[List[float]]:
        """ChromaDB calls this for query embeddings."""
        return embed_texts(input)

    @staticmethod
    def name() -> str:
        return "poisonsense_local_embedding"

    def get_config(self) -> dict:
        return {"provider": EMBEDDING_PROVIDER, "model": LOCAL_EMBEDDING_MODEL}

    @staticmethod
    def build_from_config(config: dict) -> "EmbeddingFunction":
        return EmbeddingFunction()
