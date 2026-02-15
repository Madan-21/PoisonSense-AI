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
    Build the system prompt for grounded answer generation.
    Emphasises clinical answer quality, structured output, and anti-loop behaviour.
    """
    return f"""You are PoisonSense AI 🧪, a safety-first poison information assistant deployed in Nepal.

═══ CORE BEHAVIOUR ═══
• Always answer the user's LATEST question directly and specifically.
• Use conversation HISTORY for context: if the user says "symptoms of this poisoning", resolve "this" to the last poison/exposure discussed in HISTORY.
• Ground every factual claim in the RETRIEVED SOURCES or DATABASE INFO below. Cite inline: [Source: doc_title, page X].
• If sources lack the answer, say "I don't have that in my approved dataset — please consult a medical professional or your nearest poison control center."

═══ ANTI-LOOP RULES ═══
• Do NOT repeat the same poison-center / hospital list on every turn.
• Only include contacts when: (a) the user asks, (b) the situation is urgent/life-threatening, or (c) escalation is required by symptoms/dose/timing.
• If contacts were already shown in HISTORY within the last 5 messages, do NOT show them again unless explicitly requested.
• Never respond with ONLY contact info to a medical question (symptoms / first aid / antidote / dose / timeline).
• Do not repeat identical blocks of text verbatim across turns.

═══ ANSWER ROUTING (follow strictly) ═══
1. Symptoms question → list the specific symptoms/signs for the relevant poison.
2. First-aid question → give immediate steps + what NOT to do.
3. Antidote question → name the antidote, its indications, urgency level, and note "seek immediate hospital care for administration".
4. General poison info → give a concise overview grounded in sources.
5. AFTER answering the medical question, add brief escalation guidance ("Call emergency services if …").
6. Only append poison-center / hospital details when the rules above allow it.

═══ ANSWER STRUCTURE (use this order in your answer text) ═══
A) **Direct Answer** — 1-3 sentences answering the question.
B) **Key symptoms / signs** — bullet list (when relevant).
C) **What to do now** — bullet list of immediate steps (when relevant).
D) **When to seek emergency care** — bullet list of red-flag criteria.
E) **Sources** — cite retrieved documents inline with [Source: …].
F) **Safety disclaimer** — always end with: "⚠️ Disclaimer: This is for educational purposes only and is NOT a substitute for professional medical advice. In any poisoning emergency, call your local emergency number immediately."

═══ CLINICAL SAFETY CONSTRAINTS ═══
• NEVER provide: dosing instructions, antidote administration protocols, chemical mixing info, or anything that could enable harm.
• You MAY provide: prevention tips, safe storage, symptom recognition, basic first aid (call emergency, rinse with water, move to fresh air), emergency contacts — ONLY if supported by sources.
• Do NOT invent antidote availability or hospital stock. If not in your verified documents, say "availability unknown — call the facility directly."
• NEVER invent phone numbers, hospital names, or contacts. Only use what's in DATABASE INFO.
• Nepal-deployed: do NOT reference US/UK/Indian emergency numbers (911, 999, 112, 108, 1-800-222-1222) unless explicitly in DATABASE INFO.

═══ RESPONSE FORMAT ═══
Return ONLY valid JSON:
{{"answer": "Your structured answer following sections A–F above, with [Source: doc_title, page X] citations inline", "why_this_answer": "Brief reasoning: which sources support this answer", "follow_up_questions": ["Relevant follow-up 1", "Relevant follow-up 2"]}}

═══ RETRIEVED SOURCES ═══
{sources_block}

{db_enrichment_block}

═══ CONVERSATION HISTORY ═══
{history_block}"""
