"""
Safe tools the agent can invoke.
Only prevention, lookup, and logging tools — NO dosage / mixing / harm tools.
"""

from typing import Dict, Any, Optional, List


# ── Emergency Contacts Database ────────────────────────────────────────

POISON_CONTROL_CONTACTS = {
    "nepal": {
        "country": "Nepal",
        "poison_control": "+977-1-4261466",
        "emergency": "102",
        "ambulance": "102",
        "toll_free": "1166",
        "hospitals": [
            "Tribhuvan University Teaching Hospital (TUTH)",
            "Bir Hospital",
            "Patan Hospital",
        ],
    },
    "india": {
        "country": "India",
        "poison_control": "+91-11-2658 9391",
        "emergency": "112",
        "ambulance": "108",
        "toll_free": "1800-11-6117",
        "hospitals": [
            "AIIMS Poison Control Center, New Delhi",
            "National Poisons Information Centre (NPIC)",
        ],
    },
    "usa": {
        "country": "United States",
        "poison_control": "1-800-222-1222",
        "emergency": "911",
        "ambulance": "911",
        "toll_free": "1-800-222-1222",
        "hospitals": [],
    },
    "uk": {
        "country": "United Kingdom",
        "poison_control": "0344 892 0111",
        "emergency": "999",
        "ambulance": "999",
        "toll_free": "111 (NHS)",
        "hospitals": [],
    },
}


def get_poison_control_contacts(country: str = "nepal") -> Dict[str, Any]:
    """Get poison control contacts for a country."""
    key = country.lower().strip()
    if key in POISON_CONTROL_CONTACTS:
        return POISON_CONTROL_CONTACTS[key]
    return {
        "country": country,
        "poison_control": "Contact your local poison control center",
        "emergency": "Call your local emergency number",
        "note": f"Specific contacts for '{country}' not in database. Try: nepal, india, usa, uk",
    }


def find_nearest_emergency_department(location: Optional[str] = None) -> Dict[str, Any]:
    """Provide guidance on finding nearest emergency department."""
    return {
        "action": "find_emergency_department",
        "guidance": [
            "Call 102 (Nepal) or your local emergency number",
            "Ask for the nearest hospital with a toxicology unit",
            "If driving, go to the nearest hospital emergency department",
            "Bring the container/label of the substance if available",
        ],
        "location_note": f"Near: {location}" if location else "Location not specified",
        "nepal_hospitals": [
            {"name": "TUTH - Maharajgunj", "type": "Teaching Hospital", "city": "Kathmandu"},
            {"name": "Bir Hospital", "type": "Government Hospital", "city": "Kathmandu"},
            {"name": "Patan Hospital", "type": "Hospital", "city": "Lalitpur"},
            {"name": "BP Koirala Institute", "type": "Teaching Hospital", "city": "Dharan"},
        ],
    }


def create_incident_checklist(context: str) -> Dict[str, Any]:
    """Create a checklist for a poisoning incident."""
    return {
        "checklist": [
            {"step": 1, "action": "Ensure scene safety — remove person from exposure if safe to do so", "done": False},
            {"step": 2, "action": "Call emergency services (102 in Nepal)", "done": False},
            {"step": 3, "action": "Identify the substance if possible — check labels, containers", "done": False},
            {"step": 4, "action": "Note the time of exposure", "done": False},
            {"step": 5, "action": "Record symptoms observed", "done": False},
            {"step": 6, "action": "Do NOT induce vomiting unless told by a professional", "done": False},
            {"step": 7, "action": "If skin/eye contact — rinse with clean water for 15-20 minutes", "done": False},
            {"step": 8, "action": "If inhaled — move to fresh air immediately", "done": False},
            {"step": 9, "action": "Keep the person calm and still", "done": False},
            {"step": 10, "action": "Bring substance container to the hospital", "done": False},
        ],
        "context": context,
    }


def log_incident(details: str) -> Dict[str, Any]:
    """Log an incident for record-keeping (non-medical)."""
    from datetime import datetime, timezone
    return {
        "logged": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
        "note": "This log is for informational purposes only. Always contact professional help.",
    }


def read_label_or_sds(text: str) -> Dict[str, Any]:
    """Help interpret a product label or SDS text the user provides."""
    return {
        "action": "label_interpretation",
        "input_text": text[:500],  # Limit for safety
        "guidance": [
            "Look for 'DANGER', 'WARNING', or 'CAUTION' signal words",
            "Check the 'First Aid' section for immediate steps",
            "Note the active ingredients listed",
            "Find the manufacturer's emergency phone number",
            "Check for GHS hazard pictograms",
        ],
        "note": "For full SDS interpretation, contact a toxicologist or poison control center.",
    }


# ── Tool Registry ──────────────────────────────────────────────────────

ALLOWED_TOOLS = {
    "get_poison_control_contacts": get_poison_control_contacts,
    "find_nearest_emergency_department": find_nearest_emergency_department,
    "create_incident_checklist": create_incident_checklist,
    "log_incident": log_incident,
    "read_label_or_sds": read_label_or_sds,
}

DISALLOWED_TOOLS = [
    "dosage_calculator",
    "antidote_selector",
    "antidote_administrator",
    "chemical_mixing_guide",
    "lethal_dose_calculator",
]


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a safe tool by name."""
    if tool_name in DISALLOWED_TOOLS:
        return {
            "error": f"Tool '{tool_name}' is blocked by safety policy.",
            "reason": "This tool could enable harm and is not available.",
        }
    if tool_name not in ALLOWED_TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    return ALLOWED_TOOLS[tool_name](**kwargs)
