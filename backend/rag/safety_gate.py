"""
Safety / Harm-Prevention Gate
- Classifies user queries for malicious or high-risk intent
- Provides refusal templates and safe alternatives
- Emergency escalation logic
"""

import re
from typing import Dict, Any, Optional, Tuple


# ── Malicious / Harmful Intent Patterns ─────────────────────────────────

HARM_PATTERNS = [
    # Direct harm intent
    r"\b(how\s+to\s+poison)\b",
    r"\b(best\s+poison)\b",
    r"\b(kill\s+with\s+poison)\b",
    r"\b(lethal\s+dose)\b",
    r"\b(ld50|ld\s*50)\b",
    r"\b(how\s+much\s+.*\s+kills?)\b",
    r"\b(how\s+to\s+make\s+poison)\b",
    r"\b(undetectable\s+poison)\b",
    r"\b(untraceable\s+poison)\b",
    r"\b(slow\s+acting\s+poison)\b",
    r"\b(poison\s+someone)\b",
    r"\b(mix.*chemicals?.*to\s+harm)\b",
    r"\b(create.*toxic)\b",
    r"\b(synthesize.*poison)\b",
    r"\b(weaponize)\b",
    # Dosage / antidote admin
    r"\b(antidote\s+dosage)\b",
    r"\b(how\s+much\s+antidote)\b",
    r"\b(administer\s+antidote)\b",
    r"\b(dose\s+of\s+antidote)\b",
    r"\b(give\s+antidote)\b",
    r"\b(inject.*antidote)\b",
    # Chemical mixing
    r"\b(mix.*bleach.*ammonia)\b",
    r"\b(chlorine\s+gas)\b",
    r"\b(how\s+to\s+mix\s+chemicals)\b",
    r"\b(chemical\s+weapon)\b",
    r"\b(nerve\s+agent)\b",
    # Self-harm
    r"\b(suicide.*poison)\b",
    r"\b(overdose.*how)\b",
    r"\b(want\s+to\s+die)\b",
    r"\b(kill\s+myself)\b",
    r"\b(end\s+my\s+life)\b",
]

# Compiled for performance
_harm_regex = re.compile("|".join(HARM_PATTERNS), re.IGNORECASE)

# ── Emergency Detection ────────────────────────────────────────────────

EMERGENCY_PATTERNS = [
    r"\b(swallowed|drank|ate|ingested)\b.*\b(poison|bleach|chemical|cleaner|pesticide|insecticide|rat\s*poison|antifreeze|medication|pills?)\b",
    r"\b(child|baby|kid|toddler)\b.*\b(swallowed|drank|ate)\b",
    r"\b(not\s+breathing|unconscious|seizure|convulsion|collapsed)\b",
    r"\b(burning|burns?)\b.*\b(mouth|throat|skin|eyes?)\b",
    r"\b(vomiting\s+blood|blood\s+in\s+vomit)\b",
    r"\b(emergency|urgent|immediately|right\s+now)\b.*\b(poison|toxic|chemical)\b",
    r"\b(exposed\s+to|inhaled|breathed\s+in)\b.*\b(fumes?|gas|chemical|smoke)\b",
]

_emergency_regex = re.compile("|".join(EMERGENCY_PATTERNS), re.IGNORECASE)

# ── Self-harm detection ────────────────────────────────────────────────

SELF_HARM_PATTERNS = [
    r"\b(suicide|suicidal)\b",
    r"\b(want\s+to\s+die)\b",
    r"\b(kill\s+myself)\b",
    r"\b(end\s+(my|it\s+all))\b",
    r"\b(self[- ]?harm)\b",
    r"\b(overdose)\b.*\b(myself|intentional)\b",
]

_self_harm_regex = re.compile("|".join(SELF_HARM_PATTERNS), re.IGNORECASE)

# ── Vague / Triage-needed ─────────────────────────────────────────────

VAGUE_EXPOSURE_PATTERNS = [
    r"\b(i\s+think\s+i\s+(drank|swallowed|ate|touched))\b",
    r"\b(i\s+(drank|swallowed|ate)\s+something)\b",
    r"\b(something\s+bad|feel\s+(sick|weird|dizzy|nauseous))\b",
    r"\b(exposed|exposure)\b",
    r"\b(accidental|accidentally)\b.*\b(swallowed|drank|ingested|inhaled)\b",
]

_vague_regex = re.compile("|".join(VAGUE_EXPOSURE_PATTERNS), re.IGNORECASE)


# ── Classification ─────────────────────────────────────────────────────

def classify_query(query: str) -> Dict[str, Any]:
    """
    Classify a user query for safety.
    Returns:
        {
            "risk_level": "low" | "medium" | "high",
            "is_harmful": bool,
            "is_emergency": bool,
            "is_self_harm": bool,
            "needs_triage": bool,
            "matched_pattern": str | None,
            "policy_notes": str,
        }
    """
    result = {
        "risk_level": "low",
        "is_harmful": False,
        "is_emergency": False,
        "is_self_harm": False,
        "needs_triage": False,
        "matched_pattern": None,
        "policy_notes": "",
    }

    # Check self-harm first (highest priority for compassionate response)
    self_harm_match = _self_harm_regex.search(query)
    if self_harm_match:
        result["risk_level"] = "high"
        result["is_self_harm"] = True
        result["matched_pattern"] = self_harm_match.group()
        result["policy_notes"] = "Self-harm detected. Compassionate refusal + crisis resources."
        return result

    # Check harmful intent
    harm_match = _harm_regex.search(query)
    if harm_match:
        result["risk_level"] = "high"
        result["is_harmful"] = True
        result["matched_pattern"] = harm_match.group()
        result["policy_notes"] = "Harmful intent detected. Refuse and pivot to prevention/safety."
        return result

    # Check emergency
    emergency_match = _emergency_regex.search(query)
    if emergency_match:
        result["risk_level"] = "high"
        result["is_emergency"] = True
        result["matched_pattern"] = emergency_match.group()
        result["policy_notes"] = "Potential emergency. Escalate to emergency services."
        return result

    # Check vague exposure (needs triage)
    vague_match = _vague_regex.search(query)
    if vague_match:
        result["risk_level"] = "medium"
        result["needs_triage"] = True
        result["matched_pattern"] = vague_match.group()
        result["policy_notes"] = "Vague exposure report. Triage questions needed."
        return result

    result["policy_notes"] = "General informational query."
    return result


# ── Refusal Templates ──────────────────────────────────────────────────

REFUSAL_HARMFUL = (
    "I cannot provide information that could be used to harm someone. "
    "PoisonSense AI is designed exclusively for **poison prevention and safety**.\n\n"
    "If you're concerned about a poisoning situation, I can help with:\n"
    "• 🛡️ **Prevention** — safe storage and handling\n"
    "• 🚨 **Emergency response** — what to do if exposure occurs\n"
    "• 📞 **Emergency contacts** — local poison control centers\n\n"
    "How can I help you stay safe?"
)

REFUSAL_SELF_HARM = (
    "I hear you, and I want you to know that help is available right now.\n\n"
    "**Please reach out to one of these resources immediately:**\n"
    "• 🆘 **Nepal Suicide Hotline**: 1166\n"
    "• 🌍 **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/\n"
    "• 📞 **Crisis Text Line**: Text HOME to 741741\n\n"
    "You are not alone. A trained counselor can help you through this."
)

EMERGENCY_ESCALATION = (
    "🚨 **THIS APPEARS TO BE AN EMERGENCY**\n\n"
    "**Take these steps immediately:**\n"
    "1. **Call emergency services**: 102 (Nepal) or your local emergency number\n"
    "2. **Call Poison Control**: Contact your nearest poison control center\n"
    "3. **Do NOT** induce vomiting unless instructed by a professional\n"
    "4. **Keep the container/label** of the substance if available\n"
    "5. **Stay calm** and stay with the person\n\n"
    "**Nepal Poison Information Center**: +977-1-4261466\n"
    "**Emergency (Nepal)**: 102\n\n"
    "I can provide general first-aid information from my knowledge base while you wait for professional help."
)

TRIAGE_QUESTIONS = (
    "I want to help you safely. To give you the best guidance, I need to ask a few quick questions:\n\n"
    "1. **Who is affected?** (child/teen/adult/older adult)\n"
    "2. **What substance** was involved? (name, description, or product label)\n"
    "3. **How were they exposed?** (swallowed/inhaled/skin contact/eye contact)\n"
    "4. **When did it happen?** (how long ago)\n"
    "5. **What symptoms** are present right now?\n\n"
    "⚠️ **If the person is unconscious, not breathing, or having seizures, call 102 immediately.**"
)

INSUFFICIENT_EVIDENCE = (
    "I don't have that information in my approved knowledge base. "
    "For accurate answers on this topic, please:\n\n"
    "• 📞 **Contact your local Poison Control Center**\n"
    "• 🏥 **Consult a healthcare professional**\n"
    "• 🌐 **Visit WHO Poison Prevention resources**: https://www.who.int/health-topics/poisoning\n\n"
    "I can only provide information that is directly supported by my verified medical documents."
)


def get_refusal(classification: Dict[str, Any]) -> Optional[str]:
    """Return the appropriate refusal text, or None if query is allowed."""
    if classification["is_self_harm"]:
        return REFUSAL_SELF_HARM
    if classification["is_harmful"]:
        return REFUSAL_HARMFUL
    return None


def get_emergency_escalation() -> str:
    return EMERGENCY_ESCALATION


def get_triage_questions() -> str:
    return TRIAGE_QUESTIONS


def get_insufficient_evidence() -> str:
    return INSUFFICIENT_EVIDENCE
