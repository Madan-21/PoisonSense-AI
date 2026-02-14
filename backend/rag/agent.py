"""
Agentic RAG Engine — the core brain.

Decision flow:
1. Safety gate check
2. If harmful → refuse
3. If self-harm → compassionate refusal + crisis resources
4. If emergency → escalate + retrieve first-aid from KB
5. If vague exposure → ask triage questions
6. Otherwise → retrieve from vector store, generate grounded answer with citations

Session memory is kept per session_id (short-term).
"""

import json
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from rag import vector_store
from rag.safety_gate import (
    classify_query, get_refusal, get_emergency_escalation,
    get_triage_questions, get_insufficient_evidence,
    EMERGENCY_ESCALATION, TRIAGE_QUESTIONS,
)
from rag.tools import execute_tool, get_poison_control_contacts
from rag.llm import call_llm
from rag.config import TOP_K, RELEVANCE_THRESHOLD, COLLECTIONS, DEFAULT_COLLECTION
from rag.db_tools import (
    find_nearby_hospitals_db, find_nearby_poison_centers_db,
    search_antidote_availability, get_all_hospitals_summary,
    get_all_antidotes_summary, format_hospitals_for_answer,
    format_antidotes_for_answer,
)
from rag.inference_optimization import (
    get_cache, compress_context, parallel_query_collections,
    adaptive_top_k, timed, build_compact_prompt,
)
from rag.learning import log_interaction


# ── Session Memory ─────────────────────────────────────────────────────

_sessions: Dict[str, Dict[str, Any]] = {}
MAX_HISTORY = 20  # messages per session


def _get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "id": session_id,
            "history": [],
            "triage": {},
            "advice_given": [],
            "contacted_help": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    return _sessions[session_id]


def _trim_history(session: Dict):
    if len(session["history"]) > MAX_HISTORY:
        session["history"] = session["history"][-MAX_HISTORY:]


# ── Intent → Collection Routing ────────────────────────────────────────

def _route_collections(query: str, classification: Dict) -> List[str]:
    """Decide which collections to query based on intent."""
    q_lower = query.lower()
    targets = [DEFAULT_COLLECTION]  # always include general

    # Always include learned interactions (agentic memory)
    targets.append("learned_interactions")

    if classification.get("is_emergency") or any(
        kw in q_lower for kw in ["first aid", "emergency", "help", "swallow", "inhale"]
    ):
        targets.extend(["first_aid", "emergency_escalation"])

    if any(kw in q_lower for kw in ["symptom", "sign", "feel", "effect"]):
        targets.append("symptom_recognition")

    if any(kw in q_lower for kw in ["prevent", "store", "storage", "safe", "keep away"]):
        targets.append("prevention_storage")

    if any(kw in q_lower for kw in ["nepal", "india", "hospital", "center", "contact"]):
        targets.append("regional_resources")

    # Dedupe and filter to existing collections
    existing = set(vector_store.list_collections())
    return list(dict.fromkeys(c for c in targets if c in existing)) or [DEFAULT_COLLECTION]


# ── Intent Detection for DB-backed features ────────────────────────────

_HOSPITAL_KEYWORDS = [
    "hospital", "nearest hospital", "nearby hospital", "closest hospital",
    "find hospital", "where is hospital", "emergency room", "er near",
    "location", "nearest", "nearby", "where can i go", "take me to",
    "which hospital", "hospital near me",
]

_ANTIDOTE_KEYWORDS = [
    "antidote", "anti-dote", "treatment for", "cure for", "remedy",
    "what is the antidote", "available antidote", "naloxone", "atropine",
    "pralidoxime", "n-acetylcysteine", "nac", "anti-snake venom",
    "activated charcoal", "vitamin k", "antivenom",
]

_POISON_CENTER_KEYWORDS = [
    "poison center", "poison control", "poison hotline", "helpline",
    "emergency number", "call for help", "who to call",
]


def _detect_hospital_intent(query: str) -> bool:
    """Detect if user is asking about nearby hospitals/locations."""
    q_lower = query.lower()
    return any(kw in q_lower for kw in _HOSPITAL_KEYWORDS)


def _detect_antidote_intent(query: str) -> Optional[str]:
    """Detect if user is asking about antidotes. Returns extracted antidote name or None."""
    q_lower = query.lower()
    if not any(kw in q_lower for kw in _ANTIDOTE_KEYWORDS):
        return None
    
    # Try to extract specific antidote name
    specific_antidotes = {
        "naloxone": "Naloxone",
        "atropine": "Atropine",
        "pralidoxime": "Pralidoxime",
        "n-acetylcysteine": "N-Acetylcysteine",
        "nac": "N-Acetylcysteine",
        "anti-snake venom": "Anti-Snake Venom",
        "antivenom": "Anti-Snake Venom",
        "activated charcoal": "Activated Charcoal",
        "vitamin k": "Vitamin K1",
    }
    for key, name in specific_antidotes.items():
        if key in q_lower:
            return name
    
    return "__general__"  # General antidote query


def _detect_poison_center_intent(query: str) -> bool:
    """Detect if user is asking about poison control centers."""
    q_lower = query.lower()
    return any(kw in q_lower for kw in _POISON_CENTER_KEYWORDS)


def _is_poison_related_query(query: str) -> bool:
    """Detect if the query is about poisoning/toxicology at all.
    Used to decide whether to always include Nepal emergency contacts."""
    q_lower = query.lower()
    poison_keywords = [
        "poison", "toxic", "overdose", "swallow", "ingest", "exposure",
        "venom", "snake bite", "chemical", "pesticide", "insecticide",
        "mushroom", "arsenic", "cyanide", "rat poison", "bleach",
        "first aid", "emergency", "symptom", "treatment", "antidote",
        "suspect", "accidentally", "drank", "ate", "breathe", "inhale",
        "organophosphate", "paracetamol", "acetaminophen", "drug",
    ]
    return any(kw in q_lower for kw in poison_keywords)


# ── Conversational / Greeting Detection ────────────────────────────────

_GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|howdy|sup)[\s!?.]*$",
    r"^(who\s+are\s+you|what\s+are\s+you|what\s+is\s+this|about\s+you|tell\s+me\s+about\s+yourself)",
    r"^(what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+do\s+you\s+do|help\s*me)",
    r"^(thank\s*you|thanks|thx|ty)[\s!?.]*$",
]

_GREETING_RESPONSES = {
    "greeting": (
        "Hello! 👋 I'm **PoisonSense AI**, your safety-first poison information assistant.\n\n"
        "I can help you with:\n"
        "- 🔍 Identifying poison symptoms & first-aid steps\n"
        "- 🛡️ Safe storage & prevention guidance\n"
        "- 💊 Antidote information & availability\n"
        "- 🏥 Finding nearby hospitals & emergency rooms\n"
        "- ☎️ Poison control center contacts\n\n"
        "How can I help you today?"
    ),
    "about": (
        "I'm **PoisonSense AI** 🧪 — a safety-focused poison information assistant.\n\n"
        "My purpose is to provide **evidence-based** information on:\n"
        "- Poison prevention and safe storage\n"
        "- Symptom recognition for common poisons\n"
        "- First-aid guidance and emergency response\n"
        "- Antidote availability at nearby hospitals\n"
        "- Poison control center contacts\n\n"
        "I draw from verified toxicology textbooks and a database of hospitals and antidotes. "
        "I always cite my sources so you can verify the information.\n\n"
        "⚠️ **I am NOT a substitute for professional medical advice.** "
        "In an emergency, always call your local emergency number immediately."
    ),
    "capabilities": (
        "Here's what I can help you with:\n\n"
        "🔍 **Poison Information** — Ask about any substance, symptoms, or toxicity\n"
        "🏥 **Find Hospitals** — \"Find hospitals near me\" to get the nearest emergency rooms\n"
        "💊 **Antidote Lookup** — Check which antidotes are available and where\n"
        "☎️ **Emergency Contacts** — Poison control center numbers and hotlines\n"
        "🛡️ **Prevention Tips** — Safe storage, childproofing, and handling guidance\n"
        "🚨 **Emergency First Aid** — What to do immediately after exposure\n\n"
        "Just ask me anything poison-related!"
    ),
    "thanks": "You're welcome! Stay safe. Let me know if you need anything else. 🧪",
}


def _detect_conversational(query: str) -> Optional[str]:
    """Detect greeting/about/capability queries. Returns response key or None."""
    q = query.strip().lower()
    q_clean = re.sub(r'[!?.]+$', '', q).strip()
    
    if re.match(_GREETING_PATTERNS[0], q_clean):
        return "greeting"
    if re.match(_GREETING_PATTERNS[1], q_clean):
        return "about"
    if re.match(_GREETING_PATTERNS[2], q_clean):
        return "capabilities"
    if re.match(_GREETING_PATTERNS[3], q_clean):
        return "thanks"
    return None


def _extract_coordinates(query: str, session: Dict) -> Optional[tuple]:
    """Try to extract lat/lng from query or session. Returns (lat, lng) or None."""
    # Check session for stored coordinates
    if session.get("user_location"):
        loc = session["user_location"]
        return (loc["latitude"], loc["longitude"])
    
    # Try to find coordinates in query (e.g. "27.7, 85.3")
    coord_match = re.search(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', query)
    if coord_match:
        lat, lng = float(coord_match.group(1)), float(coord_match.group(2))
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return (lat, lng)
    
    return None


def _enrich_with_db_data(query: str, session: Dict) -> Dict[str, Any]:
    """
    Check for hospital/antidote/poison-center intents and fetch DB data.
    Returns a dict with any enrichment data found.
    
    For a Nepal-deployed health system, ALWAYS include Nepal emergency contacts
    when the query is poison/health related (to prevent LLM from hallucinating
    foreign numbers like US 1-800-222-1222).
    """
    enrichment = {"hospital_data": None, "antidote_data": None, "poison_center_data": None}
    
    coords = _extract_coordinates(query, session)
    
    # Hospital/location intent
    if _detect_hospital_intent(query):
        if coords:
            hospitals = find_nearby_hospitals_db(coords[0], coords[1], radius_km=200, limit=5)
        else:
            hospitals = get_all_hospitals_summary()[:5]
        enrichment["hospital_data"] = format_hospitals_for_answer(hospitals)
    
    # Antidote intent
    antidote_name = _detect_antidote_intent(query)
    if antidote_name:
        if antidote_name == "__general__":
            antidotes = get_all_antidotes_summary()
        else:
            antidotes = search_antidote_availability(
                antidote_name,
                latitude=coords[0] if coords else None,
                longitude=coords[1] if coords else None,
            )
            if not antidotes:
                # Fallback to all antidotes
                antidotes = get_all_antidotes_summary()
        enrichment["antidote_data"] = format_antidotes_for_answer(antidotes)
    
    # Poison center intent — either explicit or always for poison-related queries
    explicit_center = _detect_poison_center_intent(query)
    # Always include Nepal emergency contacts for any poison/health query
    # This prevents the LLM from hallucinating foreign numbers
    if explicit_center or _is_poison_related_query(query):
        if coords:
            centers = find_nearby_poison_centers_db(coords[0], coords[1], radius_km=500, limit=5)
        else:
            centers = find_nearby_poison_centers_db(27.7172, 85.3240, radius_km=5000, limit=10)
        if centers:
            lines = []
            for i, c in enumerate(centers[:5], 1):
                name = c.get("name", "Unknown")
                phone = c.get("phone_primary") or c.get("phone", "")
                city = c.get("city", "")
                dist = c.get("distance_km")
                line = f"**{i}. {name}** — {city}"
                if dist is not None:
                    line += f" ({dist} km away)"
                line += f"\n   📞 {phone}"
                if c.get("toll_free_number"):
                    line += f" | Toll-free: {c['toll_free_number']}"
                if c.get("is_24_hours"):
                    line += " ✅ 24/7"
                lines.append(line)
            enrichment["poison_center_data"] = "\n\n".join(lines)
        else:
            # Fallback: hardcode Nepal emergency info so LLM never hallucinates
            enrichment["poison_center_data"] = (
                "**Nepal Poison Information Center** — Kathmandu\n"
                "   📞 +977-1-4261466\n\n"
                "**Nepal Emergency (Ambulance)**: 102\n"
                "**Nepal Mental Health Helpline**: 1166"
            )
    
    return enrichment


# ── Citation Formatter ─────────────────────────────────────────────────

# Map cryptic PDF filenames to human-readable titles
_DOC_TITLE_MAP = {
    "9241544872_eng": "WHO Guidelines on Poison Centers",
    "tp13": "IPCS/WHO Toxicology Handbook",
    "tp13-c3": "IPCS/WHO Toxicology — Chapter 3",
    "8ejN1RQJopGSNlFJ": "Clinical Toxicology Reference Guide",
    "20- FINAL- A HANDBOOK ON FORENSIC TOXICOLOGY": "Handbook of Forensic Toxicology",
    "Essential-Clinical-Toxicology-Ebook-Version-Final-High-Res": "Essential Clinical Toxicology",
}


def _clean_doc_title(raw_title: str) -> str:
    """Convert cryptic PDF filenames to human-readable titles."""
    if not raw_title or raw_title == "Unknown":
        return "Reference Document"
    # Check the map first
    if raw_title in _DOC_TITLE_MAP:
        return _DOC_TITLE_MAP[raw_title]
    # Clean up common patterns: remove file extensions, underscores, etc.
    cleaned = raw_title.replace(".pdf", "").replace("_", " ").replace("-", " ").strip()
    # Title case if it looks like a code/hash (all lowercase or random chars)
    if cleaned == cleaned.lower() or len(cleaned) < 5:
        return "Reference Document"
    return cleaned.title() if cleaned == cleaned.lower() else cleaned


def _format_sources(hits: List[Dict]) -> List[Dict]:
    """Format retrieved chunks into citation objects. Filters low-quality and deduplicates."""
    sources = []
    seen_docs = set()  # Track doc_title+page to avoid duplicates
    
    for h in hits:
        meta = h.get("metadata", {})
        text = h.get("text", "")
        score = h.get("relevance_score", 0)
        
        # Skip low-relevance sources (below 65%)
        if score < 0.65:
            continue
        
        raw_title = meta.get("doc_title", "Unknown")
        page = meta.get("page")
        
        # Skip duplicate doc+page combos
        dedup_key = f"{raw_title}|{page}"
        if dedup_key in seen_docs:
            continue
        seen_docs.add(dedup_key)
        
        # Extract a supporting quote (max 25 words)
        words = text.split()
        quote = " ".join(words[:25])
        if len(words) > 25:
            quote += "..."

        sources.append({
            "doc_title": _clean_doc_title(raw_title),
            "doc_id": meta.get("doc_id", ""),
            "source_path": meta.get("source_path", ""),
            "page": page,
            "section": meta.get("section") or None,
            "chunk_id": h.get("chunk_id", meta.get("chunk_id", "")),
            "relevance_score": score,
            "supporting_quote": quote,
        })
    
    # Limit to top 5 most relevant, de-duplicated sources
    return sources[:5]


# ── System Prompt ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are PoisonSense AI, a safety-focused poison information assistant deployed in Nepal. You MUST follow these rules strictly:

1. ONLY answer based on the RETRIEVED SOURCES and DATABASE INFORMATION provided below. NEVER use your own training knowledge.
2. For EVERY factual claim from documents, cite the source: [Source: doc_title, page X].
3. NEVER provide: dosing instructions, antidote administration details, chemical mixing instructions, or any information that could enable harm.
4. You MAY provide: prevention tips, safe storage guidance, symptom recognition, general first-aid steps (call emergency, rinse with water, move to fresh air), and emergency contact information — ONLY if supported by sources or DATABASE INFORMATION.
5. If the sources don't contain the answer, say: "I don't have that in my approved dataset" and suggest contacting a professional.
6. Keep answers concise, calm, non-judgmental, and safety-first.
7. Always end with a safety note and follow-up questions when appropriate.
8. When HOSPITAL/LOCATION DATA is provided, include the hospital details (name, phone, address, distance) in your answer. Present them clearly.
9. When ANTIDOTE AVAILABILITY DATA is provided, include the antidote details in your answer. Always note that antidote administration should ONLY be done by medical professionals.
10. When POISON CENTER DATA is provided, include the contact numbers and details prominently.
11. **CRITICAL — NO HALLUCINATED CONTACT INFORMATION**: NEVER generate, invent, or recall phone numbers, hospital names, hotline numbers, or emergency contacts from your own knowledge. If no HOSPITAL/LOCATION DATA, ANTIDOTE DATA, or POISON CENTER DATA section is provided below, do NOT include any phone numbers or hospital names in your answer. Instead say: "Please ask me to find hospitals or poison centers near you, and I can look that up from our verified database."
12. This system is deployed for users in **Nepal**. Do NOT reference US, UK, Indian, or any other country's emergency numbers (such as 1-800-222-1222, 911, 999, 112, 108) unless that data is explicitly present in the DATABASE INFORMATION below.

RESPONSE FORMAT:
You must respond in this exact JSON format:
{{
  "answer": "Your grounded answer with [Source: doc_title, page X] citations inline",
  "why_this_answer": "Brief reasoning explaining which sources support this answer",
  "follow_up_questions": ["Relevant follow-up question 1", "Relevant follow-up question 2"]
}}

RETRIEVED SOURCES:
{sources}

{db_enrichment}

CONVERSATION HISTORY:
{history}
"""


# ── Core Agent Logic ───────────────────────────────────────────────────

@timed
def ask(
    query: str,
    session_id: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Main entry point. Handles:
    - Safety classification
    - Triage for vague queries
    - Retrieval + grounded generation
    - Citation formatting
    - Location-based hospital/antidote/center lookups
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:12]

    session = _get_session(session_id)
    
    # Store user location in session if provided
    if latitude is not None and longitude is not None:
        session["user_location"] = {"latitude": latitude, "longitude": longitude}

    # ── Step 0: Conversational queries (greetings, who are you, etc.) ──
    conv_key = _detect_conversational(query)
    if conv_key:
        answer = _GREETING_RESPONSES.get(conv_key, _GREETING_RESPONSES["greeting"])
        response = _build_response(
            answer=answer,
            why="",
            sources=[],
            classification={"risk_level": "low", "policy_notes": ""},
            session_id=session_id,
            follow_up_questions=[
                "What are common household poisons?",
                "Find hospitals near me",
                "What is the antidote for paracetamol overdose?",
            ] if conv_key != "thanks" else [],
        )
        _record(session, query, answer)
        return response

    # ── Step 1: Safety gate ────────────────────────────────────────
    classification = classify_query(query)

    # Harmful → refuse
    refusal = get_refusal(classification)
    if refusal:
        response = _build_response(
            answer=refusal,
            why="Query was classified as potentially harmful or self-harm related. Safety policy triggered.",
            sources=[],
            classification=classification,
            session_id=session_id,
            refusal=refusal,
            emergency_escalation=get_emergency_escalation() if classification["is_self_harm"] else None,
        )
        _record(session, query, refusal)
        return response

    # ── Step 0: Check cache for non-emergency, non-conversational queries ──
    cache = get_cache()
    cached = cache.get(query)
    if cached and not classification["is_emergency"]:
        cached["session_id"] = session_id  # Update session ID
        _record(session, query, cached.get("answer", ""))
        return cached

    # ── Step 2: Emergency → escalate + retrieve ────────────────────
    if classification["is_emergency"]:
        hits = _retrieve(query, classification)
        filtered = vector_store.filter_by_threshold(hits, RELEVANCE_THRESHOLD)
        sources = _format_sources(filtered)
        enrichment = _enrich_with_db_data(query, session)

        emergency_text = get_emergency_escalation()
        if filtered:
            grounded = _generate_grounded_answer(query, filtered, session, enrichment)
            answer = emergency_text + "\n\n---\n\n**From my knowledge base:**\n\n" + grounded.get("answer", "")
            why = grounded.get("why_this_answer", "Emergency detected + sources retrieved.")
            follow_ups = grounded.get("follow_up_questions", [])
        else:
            answer = emergency_text
            # Append DB data even without RAG hits
            if enrichment.get("hospital_data"):
                answer += "\n\n---\n\n**🏥 Nearby Hospitals:**\n\n" + enrichment["hospital_data"]
            if enrichment.get("poison_center_data"):
                answer += "\n\n**☎️ Poison Control Centers:**\n\n" + enrichment["poison_center_data"]
            why = "Emergency detected. Escalation provided."
            follow_ups = ["What substance was involved?", "How long ago did the exposure happen?"]

        response = _build_response(
            answer=answer,
            why=why,
            sources=sources,
            classification=classification,
            session_id=session_id,
            emergency_escalation=emergency_text,
            follow_up_questions=follow_ups,
        )
        _record(session, query, answer)
        return response

    # ── Step 3: Vague exposure → triage questions ─────────────────
    if classification["needs_triage"] and not session.get("triage"):
        triage_text = get_triage_questions()
        response = _build_response(
            answer=triage_text,
            why="User reported vague exposure. Triage questions needed before retrieval.",
            sources=[],
            classification=classification,
            session_id=session_id,
            follow_up_questions=[],
        )
        _record(session, query, triage_text)
        return response

    # ── Step 4: Normal query → retrieve + generate ────────────────
    hits = _retrieve(query, classification)
    filtered = vector_store.filter_by_threshold(hits, RELEVANCE_THRESHOLD)
    sources = _format_sources(filtered)

    # Enrich with database data (hospitals, antidotes, poison centers)
    enrichment = _enrich_with_db_data(query, session)
    has_db_data = any(enrichment.get(k) for k in ["hospital_data", "antidote_data", "poison_center_data"])

    if not filtered and not has_db_data:
        insufficient = get_insufficient_evidence()
        response = _build_response(
            answer=insufficient,
            why="No sources above relevance threshold found in the knowledge base.",
            sources=[],
            classification=classification,
            session_id=session_id,
            follow_up_questions=["Could you rephrase your question?", "What specific topic are you looking for?"],
        )
        _record(session, query, insufficient)
        return response

    if not filtered and has_db_data:
        # No RAG hits but we have DB data — build a direct answer
        answer_parts = []
        if enrichment.get("hospital_data"):
            answer_parts.append("**🏥 Hospitals & Emergency Rooms:**\n\n" + enrichment["hospital_data"])
        if enrichment.get("antidote_data"):
            answer_parts.append("**💊 Antidote Availability:**\n\n" + enrichment["antidote_data"]
                + "\n\n⚠️ **Important:** Antidotes should ONLY be administered by qualified medical professionals.")
        if enrichment.get("poison_center_data"):
            answer_parts.append("**☎️ Poison Control Centers:**\n\n" + enrichment["poison_center_data"])
        
        answer = "\n\n---\n\n".join(answer_parts)
        answer += "\n\n⚠️ **Safety Note:** In any poisoning emergency, call your local emergency number immediately."
        
        response = _build_response(
            answer=answer,
            why="Answer generated from verified database records (hospitals, antidotes, poison centers).",
            sources=[],
            classification=classification,
            session_id=session_id,
            follow_up_questions=[
                "What are the symptoms of this poisoning?",
                "What first aid should I provide?",
                "Is there an antidote available?",
            ],
        )
        _record(session, query, answer)
        return response

    grounded = _generate_grounded_answer(query, filtered, session, enrichment)
    response = _build_response(
        answer=grounded.get("answer", ""),
        why=grounded.get("why_this_answer", ""),
        sources=sources,
        classification=classification,
        session_id=session_id,
        follow_up_questions=grounded.get("follow_up_questions", []),
    )
    _conf_score = response.get("confidence", {}).get("score", 0.0)
    _record(session, query, grounded.get("answer", ""),
            session_id=session_id, confidence=_conf_score,
            risk_level=classification.get("risk_level", "low"))
    
    # Cache the result for future identical queries
    cache.put(query, response)
    
    return response


# ── Internal helpers ───────────────────────────────────────────────────

def _retrieve(query: str, classification: Dict) -> List[Dict]:
    """Retrieve from relevant collections with adaptive top_k and parallel queries."""
    collections = _route_collections(query, classification)
    k = adaptive_top_k(query, TOP_K)
    
    existing = set(vector_store.list_collections())
    valid = [c for c in collections if c in existing]
    if not valid:
        valid = [DEFAULT_COLLECTION]
    
    if len(valid) == 1:
        return vector_store.query_collection(query, valid[0], k)
    
    # Use parallel collection queries for multi-collection retrieval
    return parallel_query_collections(
        query, valid, k,
        query_fn=vector_store.query_collection,
    )


def _generate_grounded_answer(
    query: str,
    hits: List[Dict],
    session: Dict,
    enrichment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Use LLM to generate a grounded answer from retrieved chunks.
    Uses compressed context and compact prompt for token efficiency."""
    
    # Compress chunks to reduce token usage
    compressed_hits = compress_context(hits, max_chars=3000)
    
    # Format sources for the prompt
    source_texts = []
    for i, h in enumerate(compressed_hits):
        meta = h.get("metadata", {})
        clean_title = _clean_doc_title(meta.get('doc_title', 'Unknown'))
        source_texts.append(
            f"[Source {i+1}] doc_title: {clean_title}, "
            f"page: {meta.get('page', '?')}, chunk_id: {h.get('chunk_id', '')}\n"
            f"Content: {h.get('text', '')}"
        )
    sources_block = "\n\n".join(source_texts)

    # Format DB enrichment data
    db_sections = []
    if enrichment:
        if enrichment.get("hospital_data"):
            db_sections.append(f"HOSPITAL/LOCATION DATA (from our verified database):\n{enrichment['hospital_data']}")
        if enrichment.get("antidote_data"):
            db_sections.append(f"ANTIDOTE AVAILABILITY DATA (from our verified database):\n{enrichment['antidote_data']}")
        if enrichment.get("poison_center_data"):
            db_sections.append(f"POISON CENTER DATA (from our verified database):\n{enrichment['poison_center_data']}")
    db_enrichment_block = "\n\n".join(db_sections) if db_sections else ""

    # Format history
    history_lines = []
    for msg in session.get("history", [])[-6:]:  # last 6 messages
        history_lines.append(f"{msg['role'].upper()}: {msg['content'][:200]}")
    history_block = "\n".join(history_lines) if history_lines else "(no prior conversation)"

    prompt = build_compact_prompt(
        sources_block=sources_block,
        history_block=history_block,
        db_enrichment_block=db_enrichment_block,
    )

    try:
        raw = call_llm(prompt, query, temperature=0.0)
        parsed = _parse_llm_response(raw)
        return parsed
    except Exception as e:
        # Fallback: return a basic answer from the top hit
        top = hits[0] if hits else {}
        return {
            "answer": f"Based on my sources: {top.get('text', '')[:300]}... [Source: {top.get('metadata', {}).get('doc_title', 'Unknown')}]",
            "why_this_answer": f"LLM generation failed ({str(e)[:100]}). Returning top retrieved passage.",
            "follow_up_questions": ["Would you like more details on this topic?"],
        }


def _parse_llm_response(raw: str) -> Dict[str, Any]:
    """Try to parse JSON from LLM response, with fallback."""
    # Try to extract JSON from the response
    try:
        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: treat entire response as the answer
    return {
        "answer": raw,
        "why_this_answer": "Response generated from retrieved sources.",
        "follow_up_questions": [],
    }


def _build_response(
    answer: str,
    why: str,
    sources: List[Dict],
    classification: Dict,
    session_id: str,
    refusal: Optional[str] = None,
    emergency_escalation: Optional[str] = None,
    follow_up_questions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the standardized response JSON with confidence metrics."""
    # Calculate confidence/accuracy score based on source relevance
    confidence = _calculate_confidence(sources, classification, bool(refusal))
    
    return {
        "answer": answer,
        "why_this_answer": why,
        "sources": sources,
        "follow_up_questions": follow_up_questions or [],
        "confidence": confidence,
        "safety": {
            "risk_level": classification.get("risk_level", "low"),
            "policy_notes": classification.get("policy_notes", ""),
            "refusal": refusal,
            "emergency_escalation": emergency_escalation,
        },
        "session_id": session_id,
    }


def _calculate_confidence(sources: List[Dict], classification: Dict, is_refusal: bool) -> Dict[str, Any]:
    """
    Calculate a confidence/accuracy metric for the response.
    Based on: number of sources, average relevance score, source agreement.
    """
    if is_refusal:
        return {"score": 1.0, "label": "Safety Policy", "basis": "safety_gate"}
    
    if not sources:
        return {"score": 0.0, "label": "No sources", "basis": "no_retrieval"}
    
    scores = [s.get("relevance_score", 0) for s in sources]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    num_sources = len(sources)
    
    # Weighted confidence:
    # - 50% from average relevance of top sources
    # - 30% from best source match
    # - 20% from number of supporting sources (more = better, up to 5)
    source_count_factor = min(num_sources / 5, 1.0)
    confidence_score = (avg_score * 0.5) + (max_score * 0.3) + (source_count_factor * 0.2)
    confidence_score = round(min(confidence_score, 1.0), 3)
    
    if confidence_score >= 0.85:
        label = "High confidence"
    elif confidence_score >= 0.70:
        label = "Good confidence"
    elif confidence_score >= 0.50:
        label = "Moderate confidence"
    else:
        label = "Low confidence"
    
    return {
        "score": confidence_score,
        "label": label,
        "basis": "retrieval",
        "num_sources": num_sources,
        "avg_relevance": round(avg_score, 3),
    }


def _record(session: Dict, user_msg: str, assistant_msg: str, session_id: str = "", confidence: float = 0.0, risk_level: str = "low"):
    """Record messages in session history and log to learning DB."""
    session["history"].append({"role": "user", "content": user_msg})
    session["history"].append({"role": "assistant", "content": assistant_msg[:500]})
    _trim_history(session)
    
    # Log to learning DB for agentic feedback loop
    try:
        log_interaction(
            question=user_msg,
            answer=assistant_msg[:2000],
            session_id=session_id or session.get("id", ""),
            confidence=confidence,
            risk_level=risk_level,
        )
    except Exception:
        pass  # Never let logging break the main flow


def reset_session(session_id: str) -> bool:
    """Reset a session's history."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
