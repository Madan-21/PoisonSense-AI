"""
Inference Optimization for PoisonSense RAG Pipeline

Optimizations:
1. Query result caching (LRU + TTL) — avoids redundant LLM calls
2. Prompt compression — reduces tokens sent to LLM
3. Concurrent collection queries — parallel retrieval from multiple collections
4. Semantic deduplication of retrieved chunks
5. Adaptive TOP_K — fewer chunks for simple queries, more for complex ones
"""

import hashlib
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

from rag.config import TOP_K, RELEVANCE_THRESHOLD


# ═══════════════════════════════════════════════════════════════════════
# 1. Query Result Cache (LRU with TTL)
# ═══════════════════════════════════════════════════════════════════════

class QueryCache:
    """
    LRU cache for RAG query results.
    Avoids redundant LLM calls for identical or near-identical queries.
    TTL ensures stale data is evicted.
    """
    
    def __init__(self, max_size: int = 200, ttl_seconds: int = 3600):
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _normalize_key(self, query: str) -> str:
        """Normalize query to canonical form for cache matching."""
        q = query.lower().strip()
        q = re.sub(r'[^\w\s]', '', q)         # Remove punctuation
        q = re.sub(r'\s+', ' ', q)             # Collapse whitespace
        return hashlib.md5(q.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result. Returns None if not found or expired."""
        key = self._normalize_key(query)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self._ttl:
                self._cache.move_to_end(key)
                self._hits += 1
                return entry["result"]
            else:
                del self._cache[key]
        self._misses += 1
        return None
    
    def put(self, query: str, result: Dict[str, Any]):
        """Cache a query result."""
        key = self._normalize_key(query)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = {
            "result": result,
            "timestamp": time.time(),
        }
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    def invalidate(self):
        """Clear all cached results."""
        self._cache.clear()
    
    @property
    def stats(self) -> Dict[str, int]:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total > 0 else 0,
            "size": len(self._cache),
        }


# Global cache instance
_query_cache = QueryCache(max_size=200, ttl_seconds=1800)  # 30 min TTL


def get_cache() -> QueryCache:
    return _query_cache


# ═══════════════════════════════════════════════════════════════════════
# 2. Prompt Compression — Reduce tokens sent to LLM
# ═══════════════════════════════════════════════════════════════════════

def compress_context(chunks: List[Dict[str, Any]], max_chars: int = 3000) -> List[Dict[str, Any]]:
    """
    Compress retrieved chunks to fit within token budget.
    
    Strategy:
    - Remove low-info chunks (very short or boilerplate)
    - Truncate long chunks to most relevant portion
    - Deduplicate semantically similar chunks
    - Cap total context size
    """
    if not chunks:
        return []
    
    # Step 1: Remove very short chunks (likely noise)
    filtered = [c for c in chunks if len(c.get("text", "")) > 50]
    
    # Step 2: Deduplicate — remove chunks with >80% word overlap
    deduped = _semantic_dedup(filtered, threshold=0.80)
    
    # Step 3: Truncate individual chunks
    truncated = []
    for chunk in deduped:
        text = chunk.get("text", "")
        if len(text) > 600:
            # Keep first and last portion (most important info is often at boundaries)
            text = text[:400] + " ... " + text[-150:]
        truncated.append({**chunk, "text": text})
    
    # Step 4: Cap total characters
    total = 0
    result = []
    for chunk in truncated:
        chunk_len = len(chunk.get("text", ""))
        if total + chunk_len > max_chars:
            remaining = max_chars - total
            if remaining > 100:
                result.append({**chunk, "text": chunk["text"][:remaining]})
            break
        result.append(chunk)
        total += chunk_len
    
    return result


def _semantic_dedup(chunks: List[Dict], threshold: float = 0.80) -> List[Dict]:
    """Remove chunks with high word overlap (semantic duplicates)."""
    if len(chunks) <= 1:
        return chunks
    
    kept = [chunks[0]]
    for chunk in chunks[1:]:
        words_new = set(chunk.get("text", "").lower().split())
        is_dup = False
        for existing in kept:
            words_old = set(existing.get("text", "").lower().split())
            if not words_new or not words_old:
                continue
            overlap = len(words_new & words_old) / min(len(words_new), len(words_old))
            if overlap >= threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(chunk)
    return kept


# ═══════════════════════════════════════════════════════════════════════
# 3. Concurrent Collection Queries
# ═══════════════════════════════════════════════════════════════════════

def parallel_query_collections(
    query: str,
    collection_names: List[str],
    top_k: int = TOP_K,
    query_fn=None,
) -> List[Dict[str, Any]]:
    """
    Query multiple vector store collections in parallel using ThreadPoolExecutor.
    Merges, deduplicates, and returns top-k results sorted by relevance.
    """
    if query_fn is None:
        from rag.vector_store import query_collection
        query_fn = query_collection
    
    if len(collection_names) <= 1:
        name = collection_names[0] if collection_names else "general"
        return query_fn(query, name, top_k)
    
    all_hits = []
    seen_ids = set()
    
    with ThreadPoolExecutor(max_workers=min(len(collection_names), 4)) as executor:
        futures = {
            executor.submit(query_fn, query, name, top_k): name
            for name in collection_names
        }
        for future in as_completed(futures):
            try:
                hits = future.result()
                for h in hits:
                    cid = h.get("chunk_id", "")
                    if cid not in seen_ids:
                        seen_ids.add(cid)
                        h["collection"] = futures[future]
                        all_hits.append(h)
            except Exception:
                continue
    
    all_hits.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return all_hits[:top_k]


# ═══════════════════════════════════════════════════════════════════════
# 4. Adaptive TOP_K — adjust retrieval count based on query complexity
# ═══════════════════════════════════════════════════════════════════════

def adaptive_top_k(query: str, base_top_k: int = TOP_K) -> int:
    """
    Dynamically adjust TOP_K based on query complexity.
    Simple/greeting queries need fewer chunks. Complex multi-topic queries need more.
    """
    q = query.lower().strip()
    word_count = len(q.split())
    
    # Very simple queries — fewer chunks needed
    if word_count <= 4:
        return max(3, base_top_k // 2)
    
    # Multi-topic or complex queries — more chunks
    complex_indicators = [
        "compare", "difference", "vs", "between", "multiple",
        "all", "list", "comprehensive", "detail", "explain",
    ]
    if any(ind in q for ind in complex_indicators):
        return min(base_top_k + 4, 15)
    
    # Default
    return base_top_k


# ═══════════════════════════════════════════════════════════════════════
# 5. Response Timing Decorator
# ═══════════════════════════════════════════════════════════════════════

def timed(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = round(time.time() - start, 3)
        if isinstance(result, dict):
            result["_latency_ms"] = int(elapsed * 1000)
        return result
    return wrapper


# ═══════════════════════════════════════════════════════════════════════
# 6. Prompt Template Optimization
# ═══════════════════════════════════════════════════════════════════════

def build_compact_prompt(
    sources_block: str,
    history_block: str,
    db_enrichment_block: str = "",
) -> str:
    """
    Build a more compact system prompt that uses fewer tokens
    while maintaining all critical safety instructions.
    """
    return f"""You are PoisonSense AI, a safety-focused poison information assistant for Nepal.

RULES:
1. Answer ONLY from RETRIEVED SOURCES and DATABASE INFO below. Never use training knowledge.
2. Cite every claim: [Source: doc_title, page X].
3. NEVER provide dosing, antidote admin details, chemical mixing, or harm-enabling info.
4. OK to provide: prevention, storage, symptom recognition, basic first aid (call emergency, rinse, fresh air), contacts — ONLY from sources.
5. If sources lack the answer, say "I don't have that in my approved dataset" and suggest a professional.
6. Be concise, calm, safety-first.
7. Include hospital/antidote/center data when provided in DATABASE INFO.
8. NEVER invent phone numbers or contacts. Only use what's in DATABASE INFO.
9. Nepal-deployed. Don't reference US/UK/Indian numbers unless in DATABASE INFO.

FORMAT (JSON):
{{"answer":"...[Source: doc_title, page X]...","why_this_answer":"...","follow_up_questions":["...","..."]}}

SOURCES:
{sources_block}

{db_enrichment_block}

HISTORY:
{history_block}"""
