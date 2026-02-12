# Agentic AI Service - PoisonSense AI Agent with RAG Architecture
"""
This module implements an Agentic AI system for poison information using RAG architecture.

RAG Architecture:
                 ┌──────────────────────────────┐
                 │            USER              │
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │   INPUT & SAFETY TRIAGE      │
                 │ - extract poison/exposure    │
                 │ - detect emergency symptoms  │
                 │ - ask for location if needed │
                 └──────────────┬───────────────┘
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
             v                                     v
┌──────────────────────────────┐     ┌──────────────────────────────┐
│  RETRIEVER: Poison Knowledge  │     │ RETRIEVER: Nepal Facilities  │
│  - poison facts & symptoms    │     │ - hospitals & labs directory │
│  - antidote availability      │     │ - geolocation + services     │
│  - do/don't safety guidance   │     │ - emergency capability       │
└──────────────┬───────────────┘     └──────────────┬───────────────┘
               │                                      │
               └──────────────┬───────────────────────┘
                              v
                 ┌──────────────────────────────┐
                 │   CONTEXT BUILDER / RANKER   │
                 │ - pick most relevant chunks  │
                 │ - merge + de-duplicate       │
                 │ - prioritize verified sources│
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │  LLM WITH STRICT SYSTEM PROMPT│
                 │ - answer ONLY from context    │
                 │ - no dosage / no procedures   │
                 │ - emergency-first messaging   │
                 └──────────────┬───────────────┘
                                │
                                v
                 ┌──────────────────────────────┐
                 │         FINAL RESPONSE        │
                 │ 1) Poison summary             │
                 │ 2) symptoms (info only)       │
                 │ 3) antidote exists? (no steps)│
                 │ 4) nearest hospital/lab list  │
                 │ 5) safety disclaimer          │
                 └──────────────────────────────┘

Tools:
- Searching poison database (RAG: Poison Knowledge)
- Finding antidotes
- Locating hospitals (RAG: Nepal Facilities)
- Getting treatment protocols
- Analyzing symptoms with ML
- Providing first aid guidance
"""

import json
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session

# RAG Data Sources - Poison Knowledge
from app.ml.data.comprehensive_toxicology_data import (
    COMPREHENSIVE_POISONS,
    SYMPTOM_POISON_MAPPING,
    EMERGENCY_NUMBERS,
    get_poison_by_symptoms,
    get_poison_details,
    get_antidote_info,
    get_first_aid,
    get_management_protocol
)

# RAG Data Sources - Poison Knowledge (Structured)
from app.ml.data.poison_knowledge import (
    POISON_KNOWLEDGE,
    retrieve_poison_by_name,
    retrieve_poison_by_symptoms,
    retrieve_poison_by_category,
    get_poison_safety_info,
    get_antidote_info as get_rag_antidote_info,
    get_emergency_signs
)

# RAG Data Sources - Nepal Facilities
from app.ml.data.nepal_facilities import (
    NEPAL_FACILITIES,
    retrieve_nearest_facilities,
    retrieve_facilities_by_antidote,
    retrieve_facilities_by_service,
    get_poison_control_hotline,
    get_facility_details,
    retrieve_diagnostic_labs,
    retrieve_labs_for_drug_screening,
    get_testing_guidance,
    FacilityType
)

from app.services.ml_service import ml_service
from app.services.location_service import LocationService
from app.models.poison import Poison
from app.models.hospital import Hospital
from app.models.poison_center import PoisonCenter


class AgentRole(Enum):
    """Roles the agent can take"""
    EMERGENCY_RESPONDER = "emergency_responder"
    MEDICAL_ADVISOR = "medical_advisor"
    INFORMATION_PROVIDER = "information_provider"
    TRIAGE_SPECIALIST = "triage_specialist"


@dataclass
class ConversationMessage:
    """A single message in the conversation"""
    role: str  # "user", "assistant", "system", "tool_result"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Maintains conversation state and context"""
    messages: List[ConversationMessage] = field(default_factory=list)
    identified_poison: Optional[str] = None
    symptoms_reported: List[str] = field(default_factory=list)
    severity_level: Optional[str] = None
    patient_info: Dict = field(default_factory=dict)
    location: Optional[Dict] = None
    tools_used: List[str] = field(default_factory=list)
    recommendations_given: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Result from a tool execution"""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None


class AgentTool:
    """Base class for agent tools"""
    name: str
    description: str
    
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            result = self.func(**kwargs)
            return ToolResult(tool_name=self.name, success=True, data=result)
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, data=None, error=str(e))


class PoisonSenseAgent:
    """
    Agentic AI for Poison Information and Emergency Guidance
    
    This agent can:
    1. Analyze symptoms and identify possible poisons
    2. Provide poison information with safety focus
    3. Look up antidotes (informational only)
    4. Find nearby hospitals, poison centers, and diagnostic labs
    5. Provide emergency action guidance
    6. Maintain conversation context
    7. Escalate emergencies appropriately
    
    ⚠️ This agent is NOT a doctor and does NOT provide treatment instructions.
    Its purpose is information and guidance only, not diagnosis or medical procedures.
    
    ==========================================================================
    SCOPE & SAFETY RULES
    ==========================================================================
    
    ✅ WHAT WE COVER:
    - Common poisons: pesticides, household cleaners, medications, plants, gases
    - Symptoms overview (early warning signs + danger signs)
    - Antidote existence (names only, NO dosages)
    - Nearest facility selection (hospitals, poison centers, labs)
    - General safety guidance ("seek medical help", "call poison control")
    
    ❌ WHAT WE DO NOT DO:
    - Medical diagnosis
    - Dosage instructions (for any medication or antidote)
    - Administration steps (how to give antidotes)
    - Home treatment procedures
    - Induce vomiting instructions (unless specifically safe)
    - Any procedure that should be done by medical professionals
    
    🚨 EMERGENCY OVERRIDE RULE:
    If ANY of these are detected:
    - Severe symptoms (unconscious, seizure, not breathing, difficulty breathing)
    - Child/infant exposure
    - Life-threatening situation
    → Immediately respond: "Go to ER now" + nearest hospitals + emergency numbers
    
    🛡️ GUARDRAILS:
    - If retrieval returns weak/empty context → say "I don't have verified info" + urge ER
    - If user asks for dosage/administration → refuse + direct to professionals
    - Always include emergency advice when risk is high
    - Always include disclaimer
    """
    
    # ==========================================================================
    # SYSTEM PROMPT - STRICT SAFETY-FOCUSED
    # ==========================================================================
    
    SYSTEM_PROMPT = """You are **PoisonSense AI** - a specialized AI assistant for poison information and emergency guidance in Nepal.

## 🎯 YOUR ROLE
You provide INFORMATION ONLY about poisons and help users find appropriate medical facilities.
You are NOT a doctor. You do NOT diagnose. You do NOT prescribe treatments.

## ✅ WHAT YOU CAN DO
- Identify possible poisons based on description
- Provide symptom information (early + danger signs)
- State whether an antidote EXISTS (name only)
- List "DO NOT DO" safety warnings
- Find nearest hospitals/poison centers based on location
- Provide emergency contact numbers

## ❌ WHAT YOU MUST NEVER DO
- Provide dosage instructions
- Explain how to administer antidotes
- Give step-by-step treatment procedures
- Diagnose medical conditions
- Recommend home remedies for poisoning
- Delay emergency care advice

## 🚨 EMERGENCY OVERRIDE
If user describes: unconsciousness, seizures, difficulty breathing, child poisoning, or any life-threatening symptom:
→ IMMEDIATELY respond: "This is a medical emergency. Call 102 or go to the nearest hospital immediately."
→ Provide nearest hospital information
→ Skip detailed information gathering

## 📋 RESPONSE TEMPLATE (Follow Strictly)
Every poison-related response MUST include:

1️⃣ **Summary** - What poison it may be, risk level (if uncertain, say so)
2️⃣ **Symptoms to Watch** - Early symptoms + Danger signs requiring emergency care
3️⃣ **Antidote** - "Exists: Yes/No/Conditional" + Name only + "Medical professionals only"
4️⃣ **What to do now** - Seek emergency care, call poison control (NO procedures)
5️⃣ **Nearest facilities** - Ranked by: distance + emergency capability + toxicology readiness
6️⃣ **Disclaimer** - "This is information only. Seek professional medical care immediately."

## 🏥 FACILITY RANKING LOGIC
When recommending facilities, rank by:
1. Distance (nearest first)
2. Emergency capability (ER, 24/7)
3. ICU/Pediatrics (if child involved)
4. Toxicology/poison readiness score

Output both: "Nearest options" AND "Best suited option"

## 🛡️ REFUSAL BEHAVIOR
If asked for dosage/administration:
→ "I cannot provide dosage or administration instructions. This must be done by medical professionals. Please call Poison Control: +977-1-4412505 or go to the nearest hospital."

If retrieval returns no verified information:
→ "I don't have verified information about this specific substance. For your safety, please seek emergency medical care immediately."
"""

    # Risk level classifications
    RISK_LEVELS = {
        "life_threatening": "🔴 Life-Threatening",
        "high": "🟠 High Risk",
        "moderate": "🟡 Moderate Risk",
        "low": "🟢 Low Risk",
        "unknown": "⚪ Unknown - Seek Medical Evaluation"
    }
    
    # ==========================================================================
    # EMERGENCY DETECTION KEYWORDS
    # ==========================================================================

    EMERGENCY_KEYWORDS = [
        "unconscious", "not breathing", "seizure", "cardiac arrest",
        "difficulty breathing", "blue lips", "turning blue", "cyanosis",
        "no pulse", "collapse", "unresponsive", "dying", "critical",
        "child poisoning", "baby ate", "toddler swallowed", "kid drank",
        "breathing difficulty", "can't breathe", "gasping", "choking",
        "convulsion", "fits", "foaming", "foam from mouth"
    ]
    
    # Severe symptoms that trigger emergency override
    SEVERE_EMERGENCY_SYMPTOMS = [
        "unconscious", "seizure", "not breathing", "difficulty breathing",
        "cardiac arrest", "no pulse", "cyanosis", "blue lips", "collapse",
        "unresponsive", "choking", "gasping", "convulsion", "fits",
        "foaming at mouth", "paralysis", "can't move"
    ]
    
    # Child-related keywords (always trigger emergency override)
    CHILD_EMERGENCY_KEYWORDS = [
        "child", "baby", "infant", "toddler", "kid", "minor",
        "my son", "my daughter", "year old", "months old"
    ]
    
    # ==========================================================================
    # PROHIBITED CONTENT PATTERNS (Guardrails)
    # ==========================================================================
    
    PROHIBITED_REQUEST_PATTERNS = [
        "how much", "dosage", "dose", "how to give", "how to administer",
        "inject", "injection", "IV dose", "infusion rate", "loading dose",
        "maintenance dose", "mg/kg", "milligrams", "treatment protocol",
        "how to treat at home", "home remedy", "home treatment"
    ]
    
    POISON_KEYWORDS = {
        "organophosphate": ["pesticide", "insecticide", "malathion", "parathion", "farm spray", "bug spray", "op poison"],
        "carbamate": ["carbamate", "sevin", "carbaryl", "baygon"],
        "paraquat": ["paraquat", "gramoxone", "herbicide", "weedkiller"],
        "acetaminophen": ["paracetamol", "tylenol", "crocin", "panadol", "fever medicine", "medicine", "swallowed medicine"],
        "opioid": ["morphine", "heroin", "fentanyl", "oxycodone", "codeine", "tramadol", "brown sugar", "drug overdose", "overdose"],
        "snake_neurotoxic": ["snake bite", "cobra", "krait", "serpent", "snake"],
        "snake_hemotoxic": ["viper", "viper bite", "russell's viper", "pit viper"],
        "methanol": ["wood alcohol", "spurious liquor", "hooch", "local alcohol", "country liquor"],
        "ethylene_glycol": ["antifreeze", "coolant", "brake fluid"],
        "warfarin_rodenticide": ["rat poison", "rodenticide", "ratol", "mouse poison"],
        "hydrocarbon": ["kerosene", "petrol", "diesel", "fuel", "paraffin", "gasoline"],
        "corrosive_acid": ["acid", "toilet cleaner", "battery acid", "drain cleaner acid"],
        "corrosive_alkali": ["alkali", "bleach", "drain cleaner", "oven cleaner", "caustic"],
        "oleander": ["oleander", "kaner", "yellow flower plant", "plant ingestion"],
        "mushroom_amatoxin": ["mushroom", "wild mushroom", "toadstool", "death cap"],
        "benzodiazepine": ["sleeping pill", "valium", "diazepam", "xanax", "alprazolam"],
        "child_poisoning": ["child swallowed", "child ate", "baby ate", "toddler swallowed", "kid drank", "child ingestion"],
    }

    def __init__(self, db: Session):
        self.db = db
        self.location_service = LocationService(db)
        self.context = ConversationContext()
        self.tools = self._initialize_tools()
        
    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize all available tools"""
        return {
            "analyze_symptoms": AgentTool(
                name="analyze_symptoms",
                description="Analyze symptoms using ML model and database to identify possible poisoning",
                func=self._tool_analyze_symptoms
            ),
            "get_poison_info": AgentTool(
                name="get_poison_info",
                description="Get comprehensive information about a specific poison",
                func=self._tool_get_poison_info
            ),
            "get_first_aid": AgentTool(
                name="get_first_aid",
                description="Get first aid instructions for a specific poison",
                func=self._tool_get_first_aid
            ),
            "get_antidote": AgentTool(
                name="get_antidote",
                description="Get antidote information and dosing for a poison",
                func=self._tool_get_antidote
            ),
            "get_management_protocol": AgentTool(
                name="get_management_protocol",
                description="Get detailed hospital management protocol",
                func=self._tool_get_management_protocol
            ),
            "find_nearby_hospitals": AgentTool(
                name="find_nearby_hospitals",
                description="Find nearby hospitals with toxicology capabilities",
                func=self._tool_find_nearby_hospitals
            ),
            "find_poison_centers": AgentTool(
                name="find_poison_centers",
                description="Find nearby poison control centers",
                func=self._tool_find_poison_centers
            ),
            "get_emergency_numbers": AgentTool(
                name="get_emergency_numbers",
                description="Get emergency contact numbers",
                func=self._tool_get_emergency_numbers
            ),
            "assess_severity": AgentTool(
                name="assess_severity",
                description="Assess the severity of poisoning case",
                func=self._tool_assess_severity
            ),
            "search_poison_database": AgentTool(
                name="search_poison_database",
                description="Search the comprehensive poison database",
                func=self._tool_search_poison_database
            ),
            "rag_retrieve_by_symptoms": AgentTool(
                name="rag_retrieve_by_symptoms",
                description="RAG Retriever: Find poisons based on symptoms",
                func=self._tool_rag_retrieve_by_symptoms
            ),
            "rag_find_facilities": AgentTool(
                name="rag_find_facilities",
                description="RAG Retriever: Find facilities by location and capability",
                func=self._tool_rag_find_facilities
            ),
        }
    
    # ==========================================================================
    # TOOL IMPLEMENTATIONS
    # ==========================================================================
    
    def _tool_analyze_symptoms(self, symptoms: str) -> Dict:
        """
        Analyze symptoms using ML model, RAG retrieval, and database.
        
        This is the main symptom analysis tool that combines:
        1. ML model prediction
        2. RAG symptom-based retrieval
        3. Database symptom matching
        """
        # First, try ML model
        ml_result = ml_service.predict(symptoms)
        
        # RAG: Retrieve poisons by symptoms
        symptom_list = [s.strip() for s in symptoms.replace(',', ' ').split() if len(s.strip()) > 2]
        rag_matches = retrieve_poison_by_symptoms(symptom_list, limit=3)
        
        # Also search comprehensive database
        db_matches = get_poison_by_symptoms(symptom_list)
        
        # Combine results
        combined = {
            "ml_prediction": ml_result,
            "rag_matches": rag_matches,
            "database_matches": db_matches[:5],
            "confidence_assessment": self._assess_prediction_confidence(ml_result, db_matches)
        }
        
        # Update context
        self.context.symptoms_reported.extend(symptom_list)
        if ml_result.get("primary_prediction"):
            self.context.identified_poison = ml_result["primary_prediction"].get("poison_name")
        
        return combined
    
    def _tool_get_poison_info(self, poison_name: str) -> Dict:
        """
        Get comprehensive poison information using RAG retrieval.
        
        Sources:
        1. RAG Poison Knowledge database (structured)
        2. Comprehensive toxicology data
        3. SQL database (fallback)
        """
        # Normalize poison name
        poison_id = self._normalize_poison_name(poison_name)
        
        # Try RAG Poison Knowledge first (structured data)
        rag_poison = retrieve_poison_by_name(poison_name)
        
        # Get from comprehensive database
        poison_data = get_poison_details(poison_id)
        
        # Merge RAG data with comprehensive data
        if rag_poison:
            # Enhance poison_data with RAG structured info
            if not poison_data:
                poison_data = {}
            
            poison_data.update({
                "name": rag_poison.get("poison_name", poison_data.get("name")),
                "category": rag_poison.get("category", poison_data.get("category")),
                "common_names": rag_poison.get("aliases", poison_data.get("common_names", [])),
                "risk_level": rag_poison.get("risk_level"),
                "routes": rag_poison.get("routes", []),
                "symptoms_immediate": rag_poison.get("typical_symptoms_early", poison_data.get("symptoms_immediate", [])),
                "symptoms_delayed": rag_poison.get("danger_signs_emergency", poison_data.get("symptoms_delayed", [])),
                "antidote_exists": rag_poison.get("antidote_exists"),
                "antidote_names": rag_poison.get("antidote_names", []),
                "do_not_do": rag_poison.get("do_not_do", []),
                "clinical_notes": rag_poison.get("clinical_notes"),
                "source_refs": rag_poison.get("source_refs", [])
            })
            
            # Preserve antidote from comprehensive data if available
            if not poison_data.get("antidote") and rag_poison.get("antidote_names"):
                poison_data["antidote"] = {
                    "primary": rag_poison["antidote_names"][0] if rag_poison["antidote_names"] else None,
                    "available": rag_poison.get("antidote_exists") == "Yes"
                }
        
        if not poison_data:
            # Try SQL database
            db_poison = self.db.query(Poison).filter(
                Poison.name.ilike(f"%{poison_name}%")
            ).first()
            
            if db_poison:
                poison_data = {
                    "name": db_poison.name,
                    "category": db_poison.category.value if db_poison.category else None,
                    "common_names": db_poison.common_names,
                    "symptoms_immediate": db_poison.symptoms_immediate,
                    "symptoms_delayed": db_poison.symptoms_delayed,
                    "antidote": db_poison.antidote,
                    "first_aid": db_poison.first_aid,
                    "management_protocol": db_poison.management_protocol
                }
        
        return poison_data or {"error": f"Poison '{poison_name}' not found in database"}
    
    def _tool_get_first_aid(self, poison_name: str) -> Dict:
        """Get first aid instructions"""
        poison_id = self._normalize_poison_name(poison_name)
        first_aid = get_first_aid(poison_id)
        
        if not first_aid:
            # Get from comprehensive database
            poison_data = get_poison_details(poison_id)
            first_aid = poison_data.get("first_aid", [])
        
        # Add general first aid if specific not found
        if not first_aid:
            first_aid = [
                "1. Remove person from source of exposure",
                "2. Call emergency services immediately: 102",
                "3. Do not induce vomiting unless instructed by poison control",
                "4. If unconscious, place in recovery position",
                "5. Bring substance container to hospital if possible",
                "6. Call Poison Control: +977-1-4412505"
            ]
        
        return {
            "poison": poison_name,
            "first_aid_steps": first_aid,
            "emergency_number": "102",
            "poison_control": "+977-1-4412505"
        }
    
    def _tool_get_antidote(self, poison_name: str) -> Dict:
        """Get antidote information"""
        poison_id = self._normalize_poison_name(poison_name)
        antidote_info = get_antidote_info(poison_id)
        
        if not antidote_info:
            poison_data = get_poison_details(poison_id)
            antidote_info = poison_data.get("antidote", {})
        
        return {
            "poison": poison_name,
            "antidote": antidote_info,
            "note": "Antidote administration should be done by medical professionals only"
        }
    
    def _tool_get_management_protocol(self, poison_name: str) -> Dict:
        """Get hospital management protocol"""
        poison_id = self._normalize_poison_name(poison_name)
        protocol = get_management_protocol(poison_id)
        
        if not protocol:
            poison_data = get_poison_details(poison_id)
            protocol = poison_data.get("management_protocol", [])
        
        # Get additional info
        poison_data = get_poison_details(poison_id)
        
        return {
            "poison": poison_name,
            "management_protocol": protocol,
            "tests_required": poison_data.get("tests_required", []),
            "monitoring_parameters": poison_data.get("monitoring_parameters", []),
            "contraindications": poison_data.get("contraindications", []),
            "data_sources": poison_data.get("data_sources", [])
        }
    
    def _tool_find_nearby_hospitals(self, latitude: float = None, longitude: float = None, antidote: str = None) -> List[Dict]:
        """
        Find nearby hospitals using RAG Facilities retriever.
        
        Ranking algorithm:
        1. Filter by distance
        2. Filter by emergency capability
        3. Rank by: poison_case_ready_score + proximity bonus
        """
        hospitals = []
        
        if latitude and longitude:
            # Use RAG retriever for location-based search
            facilities = retrieve_nearest_facilities(
                latitude=latitude,
                longitude=longitude,
                facility_type=FacilityType.HOSPITAL,
                max_distance_km=50,
                min_poison_score=50,
                require_emergency=True,
                limit=10
            )
            
            hospitals = [
                {
                    "id": f["facility_id"],
                    "name": f["facility_name"],
                    "phone": f["phone_primary"],
                    "address": f["address"],
                    "distance_km": f["distance_km"],
                    "suitability_score": f["suitability_score"],
                    "poison_case_ready_score": f["poison_case_ready_score"],
                    "has_toxicology": f["has_toxicology"],
                    "services": f["services"],
                    "antidote_stock": f["antidote_stock_notes"],
                    "is_24_hours": f["open_24_7"],
                    "latitude": f["latitude"],
                    "longitude": f["longitude"],
                    "notes": f["notes"]
                } for f in facilities
            ]
            
            # If antidote specified, also search by antidote availability
            if antidote:
                antidote_facilities = retrieve_facilities_by_antidote(antidote, limit=5)
                for af in antidote_facilities:
                    if af["facility_id"] not in [h["id"] for h in hospitals]:
                        hospitals.append({
                            "id": af["facility_id"],
                            "name": af["facility_name"],
                            "phone": af["phone_primary"],
                            "address": af["address"],
                            "antidote_stock": af["antidote_stock_notes"],
                            "has_antidote": True,
                            "is_24_hours": af["open_24_7"]
                        })
        else:
            # No location - return best hospitals from RAG database
            for fid, facility in NEPAL_FACILITIES.items():
                if facility["facility_type"] == FacilityType.HOSPITAL:
                    hospitals.append({
                        "id": fid,
                        "name": facility["facility_name"],
                        "phone": facility["phone_primary"],
                        "address": f"{facility['address_line']}, {facility['district']}",
                        "poison_case_ready_score": facility["poison_case_ready_score"],
                        "has_toxicology": facility["has_toxicology"],
                        "services": facility["services"],
                        "is_24_hours": facility["open_24_7"]
                    })
            
            # Sort by poison readiness score
            hospitals.sort(key=lambda x: -x.get("poison_case_ready_score", 0))
            hospitals = hospitals[:10]
            
            # Also try database fallback
            if not hospitals:
                db_hospitals = self.db.query(Hospital).filter(
                    Hospital.is_active == True,
                    Hospital.city.ilike("%Kathmandu%")
                ).limit(10).all()
                
                hospitals = [
                    {
                        "id": h.id,
                        "name": h.name,
                        "phone": h.emergency_phone or h.phone,
                        "address": f"{h.address}, {h.city}",
                        "facilities": h.facilities,
                        "is_24_hours": h.is_24_hours
                    } for h in db_hospitals
                ]
        
        return hospitals
    
    def _tool_find_poison_centers(self, latitude: float = None, longitude: float = None) -> List[Dict]:
        """
        Find nearby poison control centers using RAG Facilities retriever.
        """
        centers = []
        
        if latitude and longitude:
            # Use RAG retriever for location-based search
            facilities = retrieve_nearest_facilities(
                latitude=latitude,
                longitude=longitude,
                facility_type=FacilityType.POISON_CENTER,
                max_distance_km=200,
                min_poison_score=80,
                require_emergency=False,
                limit=5
            )
            
            centers = [
                {
                    "id": f["facility_id"],
                    "name": f["facility_name"],
                    "phone": f["phone_primary"],
                    "toll_free": f.get("phone_secondary", "1102"),
                    "address": f["address"],
                    "distance_km": f.get("distance_km"),
                    "services": f["services"],
                    "is_24_hours": f["open_24_7"],
                    "notes": f["notes"]
                } for f in facilities
            ]
        
        # Always include National Poison Control Hotline
        npic = get_poison_control_hotline()
        if not any(c.get("id") == "PC001" for c in centers):
            centers.insert(0, {
                "id": "PC001",
                "name": npic["name"],
                "phone": npic["hotline"],
                "toll_free": npic["toll_free"],
                "services": npic["services"],
                "is_24_hours": True,
                "notes": npic["notes"]
            })
        
        # Fallback to database if no RAG results
        if len(centers) <= 1:
            db_centers = self.db.query(PoisonCenter).filter(
                PoisonCenter.country == "Nepal"
            ).all()
            
            for c in db_centers:
                if c.id not in [center.get("id") for center in centers]:
                    centers.append({
                        "id": c.id,
                        "name": c.name,
                        "phone": c.phone_primary,
                        "toll_free": c.toll_free_number,
                        "address": f"{c.address}, {c.city}",
                        "is_24_hours": c.is_24_hours
                    })
        
        return centers
    
    def _tool_find_diagnostic_labs(self, latitude: float = None, longitude: float = None, test_type: str = None) -> Dict:
        """
        Find diagnostic laboratories for clinical testing.
        
        Used for non-emergency cases where doctors need to refer patients
        for poison-related clinical testing (CBC, electrolytes, toxicology panels).
        
        Args:
            latitude, longitude: Optional location for proximity sorting
            test_type: Specific test to search for (e.g., "drug screen", "CBC", "toxicology")
        """
        result = {
            "labs": [],
            "drug_screening_labs": [],
            "testing_guidance": None
        }
        
        # Get diagnostic labs
        labs = retrieve_diagnostic_labs(
            latitude=latitude,
            longitude=longitude,
            test_type=test_type,
            require_toxicology=False,
            limit=10
        )
        result["labs"] = labs
        
        # Get labs specifically for drug screening
        drug_labs = retrieve_labs_for_drug_screening(limit=5)
        result["drug_screening_labs"] = drug_labs
        
        # Get testing guidance based on query
        if test_type:
            result["testing_guidance"] = get_testing_guidance(test_type)
        else:
            result["testing_guidance"] = get_testing_guidance("routine")
        
        return result
    
    def _tool_get_emergency_numbers(self, country: str = "nepal") -> Dict:
        """Get emergency numbers"""
        return EMERGENCY_NUMBERS.get(country.lower(), EMERGENCY_NUMBERS["nepal"])
    
    def _tool_assess_severity(self, symptoms: str, poison_name: str = None) -> Dict:
        """
        Assess severity of poisoning
        
        Risk Levels:
        - Life-Threatening: Immediate danger to life
        - High: Serious condition requiring urgent care
        - Moderate: Medical attention needed
        - Low: Monitor and seek guidance
        """
        symptoms_lower = symptoms.lower()
        
        # Check for critical symptoms (Life-Threatening)
        critical_symptoms = [
            "not breathing", "unconscious", "seizure", "cardiac arrest",
            "no pulse", "cyanosis", "respiratory failure", "coma",
            "convulsion", "fits", "gasping", "choking"
        ]
        
        # Severe symptoms (High Risk)
        severe_symptoms = [
            "difficulty breathing", "vomiting blood", "severe pain",
            "paralysis", "collapse", "blood pressure drop", "arrhythmia",
            "chest pain", "bleeding", "blue lips", "turning blue"
        ]
        
        moderate_symptoms = [
            "vomiting", "confusion", "drowsiness", "tremor",
            "sweating", "diarrhea", "abdominal pain"
        ]
        
        if any(s in symptoms_lower for s in critical_symptoms):
            severity = "CRITICAL"
            action = "CALL 102 IMMEDIATELY - Life-threatening emergency"
        elif any(s in symptoms_lower for s in severe_symptoms):
            severity = "SEVERE"
            action = "Go to nearest hospital emergency immediately"
        elif any(s in symptoms_lower for s in moderate_symptoms):
            severity = "MODERATE"
            action = "Seek medical attention promptly, call poison control"
        else:
            severity = "MILD"
            action = "Monitor closely, call poison control for guidance"
        
        self.context.severity_level = severity
        
        return {
            "severity": severity,
            "recommended_action": action,
            "emergency_number": "102",
            "poison_control": "+977-1-4412505",
            "assessed_symptoms": symptoms
        }
    
    def _tool_search_poison_database(self, query: str) -> List[Dict]:
        """Search poison database by name, category, or symptoms"""
        results = []
        query_lower = query.lower()
        
        for poison_id, poison_data in COMPREHENSIVE_POISONS.items():
            score = 0
            
            # Check name
            if query_lower in poison_data.get("name", "").lower():
                score += 3
            
            # Check common names
            for name in poison_data.get("common_names", []):
                if query_lower in name.lower():
                    score += 2
                    break
            
            # Check category
            if query_lower in poison_data.get("category", "").lower():
                score += 1
            
            # Check common sources
            for source in poison_data.get("common_sources", []):
                if query_lower in source.lower():
                    score += 1
                    break
            
            if score > 0:
                results.append({
                    "poison_id": poison_id,
                    "name": poison_data.get("name"),
                    "category": poison_data.get("category"),
                    "relevance_score": score,
                    "common_names": poison_data.get("common_names", [])[:5]
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:10]
    
    def _tool_rag_retrieve_by_symptoms(self, symptoms: List[str]) -> List[Dict]:
        """
        RAG Retriever: Find poisons based on symptoms.
        
        This tool uses the structured poison knowledge database to find
        possible poisons that match the given symptoms.
        """
        return retrieve_poison_by_symptoms(symptoms, limit=5)
    
    def _tool_rag_find_facilities(
        self,
        latitude: float = None,
        longitude: float = None,
        facility_type: str = None,
        service: str = None,
        antidote: str = None
    ) -> List[Dict]:
        """
        RAG Retriever: Find facilities based on location and capability.
        
        This is the main facility search tool that combines:
        - Location-based search (nearest)
        - Service-based search (toxicology, dialysis, etc.)
        - Antidote availability search
        """
        results = []
        
        # Convert facility_type string to enum if provided
        ftype = None
        if facility_type:
            facility_type_lower = facility_type.lower()
            if "hospital" in facility_type_lower:
                ftype = FacilityType.HOSPITAL
            elif "poison" in facility_type_lower or "center" in facility_type_lower:
                ftype = FacilityType.POISON_CENTER
            elif "lab" in facility_type_lower:
                ftype = FacilityType.LAB
        
        # Location-based search
        if latitude and longitude:
            facilities = retrieve_nearest_facilities(
                latitude=latitude,
                longitude=longitude,
                facility_type=ftype,
                max_distance_km=100,
                min_poison_score=50,
                require_emergency=True,
                limit=10
            )
            results.extend(facilities)
        
        # Service-based search
        if service:
            service_facilities = retrieve_facilities_by_service(service, limit=5)
            for sf in service_facilities:
                if sf["facility_id"] not in [r.get("facility_id") for r in results]:
                    results.append(sf)
        
        # Antidote-based search
        if antidote:
            antidote_facilities = retrieve_facilities_by_antidote(antidote, limit=5)
            for af in antidote_facilities:
                if af["facility_id"] not in [r.get("facility_id") for r in results]:
                    results.append(af)
        
        # If no specific criteria, return top facilities
        if not results:
            for fid, facility in NEPAL_FACILITIES.items():
                results.append({
                    "facility_id": fid,
                    "facility_name": facility["facility_name"],
                    "facility_type": facility["facility_type"].value if isinstance(facility["facility_type"], FacilityType) else facility["facility_type"],
                    "poison_case_ready_score": facility["poison_case_ready_score"],
                    "phone_primary": facility["phone_primary"],
                    "address": f"{facility['address_line']}, {facility['district']}"
                })
            results.sort(key=lambda x: -x.get("poison_case_ready_score", 0))
            results = results[:10]
        
        return results
    
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _normalize_poison_name(self, name: str) -> str:
        """Normalize poison name to database key"""
        name_lower = name.lower().strip()
        
        # Direct mappings
        mappings = {
            "paracetamol": "acetaminophen",
            "tylenol": "acetaminophen",
            "organophosphorus": "organophosphate",
            "op poisoning": "organophosphate",
            "snake bite": "snake_neurotoxic",
            "cobra": "snake_neurotoxic",
            "krait": "snake_neurotoxic",
            "viper": "snake_hemotoxic",
            "rat poison": "warfarin_rodenticide",
            "kerosene": "hydrocarbon",
            "petrol": "hydrocarbon",
            "acid": "corrosive_acid",
            "alkali": "corrosive_alkali",
            "death cap": "mushroom_amatoxin",
            "amanita": "mushroom_amatoxin"
        }
        
        for key, value in mappings.items():
            if key in name_lower:
                return value
        
        # Try to match directly
        for poison_id in COMPREHENSIVE_POISONS.keys():
            if name_lower in poison_id or poison_id in name_lower:
                return poison_id
        
        return name_lower.replace(" ", "_")
    
    def _assess_prediction_confidence(self, ml_result: Dict, db_matches: List[Dict]) -> str:
        """Assess overall prediction confidence"""
        ml_confidence = ml_result.get("primary_prediction", {}).get("confidence", 0)
        db_score = db_matches[0]["score"] if db_matches else 0
        
        if ml_confidence > 0.7 and db_score >= 3:
            return "HIGH - Strong match from both ML model and symptom database"
        elif ml_confidence > 0.5 or db_score >= 2:
            return "MODERATE - Partial match, consider alternative diagnoses"
        else:
            return "LOW - Limited matching, recommend professional evaluation"
    
    def _is_emergency(self, message: str) -> bool:
        """
        🚨 EMERGENCY OVERRIDE RULE
        Check if message indicates emergency based on:
        1. Severe symptoms (unconsciousness, seizures, breathing difficulty, cardiac arrest)
        2. Child exposure (any mention of child + poison/ingestion)
        
        If TRUE → immediately redirect to ER with emergency guidance
        """
        message_lower = message.lower()
        
        # Check for severe emergency symptoms
        has_severe_symptoms = any(keyword in message_lower for keyword in self.SEVERE_EMERGENCY_SYMPTOMS)
        
        # Check for child-related keywords combined with poison/ingestion context
        has_child_keywords = any(keyword in message_lower for keyword in self.CHILD_EMERGENCY_KEYWORDS)
        poison_context_keywords = [
            "swallowed", "ate", "drank", "ingested", "poison", "exposure",
            "overdose", "bite", "chemical", "medicine", "tablet", "pill"
        ]
        has_poison_context = any(keyword in message_lower for keyword in poison_context_keywords)
        
        # Child + poison context = EMERGENCY
        child_emergency = has_child_keywords and has_poison_context
        
        # Standard emergency keywords check
        standard_emergency = any(keyword in message_lower for keyword in self.EMERGENCY_KEYWORDS)
        
        return has_severe_symptoms or child_emergency or standard_emergency
    
    def _is_prohibited_request(self, message: str) -> bool:
        """
        🚫 GUARDRAIL: Check if user is asking for prohibited information
        Prohibited:
        - Specific dosage/dose amounts
        - How to administer antidotes
        - Home treatment procedures
        - Medical diagnosis
        """
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in self.PROHIBITED_REQUEST_PATTERNS)
    
    def _get_refusal_response(self, message: str) -> Dict:
        """
        Generate polite refusal for prohibited requests
        Redirect to professional care
        """
        response_text = """I understand you're looking for specific treatment information. 🩺

However, I'm designed to provide **poison awareness and guidance only**, not specific medical treatment.

### ❌ What I Cannot Provide:
- Specific dosage or dose amounts
- Instructions for administering antidotes
- Home treatment procedures
- Medical diagnosis

### ✅ What I Recommend:
1. **Call Poison Control immediately:** +977-1-4412505
2. **Go to the nearest hospital** for professional medical care
3. **Bring the container/label** of the substance if available

> **"Antidotes and treatments must only be administered by trained medical professionals who can assess the patient directly."**

---

🏥 *Would you like me to help find the nearest hospital or provide general poison information instead?*"""

        return {
            "message": response_text,
            "is_emergency": False,
            "is_refusal": True,
            "tools_used": ["guardrail_check"],
            "emergency_numbers": {
                "poison_control": "+977-1-4412505",
                "emergency": "102",
                "toll_free": "1102"
            }
        }
    
    def _identify_poison_from_message(self, message: str) -> Optional[str]:
        """Try to identify poison from message keywords"""
        message_lower = message.lower()
        
        for poison_id, keywords in self.POISON_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return poison_id
        
        return None
    
    def _extract_symptoms(self, message: str) -> List[str]:
        """Extract symptoms from message"""
        symptoms = []
        message_lower = message.lower()
        
        # Check against known symptoms
        for symptom in SYMPTOM_POISON_MAPPING.keys():
            if symptom in message_lower:
                symptoms.append(symptom)
        
        return symptoms
    
    # ==========================================================================
    # MAIN AGENT LOGIC
    # ==========================================================================
    
    async def process_message(
        self,
        user_message: str,
        latitude: float = None,
        longitude: float = None
    ) -> Dict:
        """
        Main entry point - Process user message and generate response
        
        This is the core agentic loop:
        1. Check for emergency keywords (Emergency Override Rule)
        2. Understand intent
        3. Determine which tools to use
        4. Execute tools
        5. Synthesize response following structured format
        6. Update context
        
        🌍 Location Awareness Rules:
        - Use user's current or provided location
        - Prefer government hospitals, emergency departments
        - If location unavailable, ask user to share city/region
        """
        # Store location
        if latitude and longitude:
            self.context.location = {"latitude": latitude, "longitude": longitude}
        
        # Add user message to context
        self.context.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        
        # 🚨 EMERGENCY OVERRIDE RULE
        # If severe symptoms, unconsciousness, seizures, breathing difficulty,
        # or child poisoning is detected, immediately respond with emergency guidance
        if self._is_emergency(user_message):
            return await self._handle_emergency(user_message)
        
        # 🚫 GUARDRAIL: Check for prohibited requests (dosage, treatment procedures)
        if self._is_prohibited_request(user_message):
            refusal = self._get_refusal_response(user_message)
            self.context.messages.append(ConversationMessage(
                role="assistant",
                content=refusal["message"]
            ))
            return refusal
        
        # Identify intent and plan actions
        intent = self._analyze_intent(user_message)
        
        # Execute planned actions
        tool_results = await self._execute_plan(intent, user_message)
        
        # Generate response following structured format
        response = self._synthesize_response(intent, tool_results, user_message)
        
        # Add assistant response to context
        self.context.messages.append(ConversationMessage(
            role="assistant",
            content=response["message"]
        ))
        
        return response
    
    async def _handle_emergency(self, message: str) -> Dict:
        """
        Handle emergency situations with immediate response
        
        🚨 EMERGENCY OVERRIDE RULE:
        If user describes severe symptoms, unconsciousness, seizures, 
        breathing difficulty, or child poisoning, immediately respond 
        with emergency guidance.
        """
        severity_result = self._tool_assess_severity(message)
        emergency_numbers = self._tool_get_emergency_numbers()
        
        # Get poison info if identified
        poison_id = self._identify_poison_from_message(message)
        poison_info = None
        first_aid = None
        antidote_info = None
        
        if poison_id:
            poison_info = get_poison_details(poison_id)
            first_aid_result = self._tool_get_first_aid(poison_id)
            first_aid = first_aid_result.get("first_aid_steps")
            antidote_result = self._tool_get_antidote(poison_id)
            antidote_info = antidote_result.get("antidote")
        
        # Find nearby hospitals
        hospitals = []
        poison_centers = []
        if self.context.location:
            hospitals = self._tool_find_nearby_hospitals(
                self.context.location.get("latitude"),
                self.context.location.get("longitude")
            )
            poison_centers = self._tool_find_poison_centers(
                self.context.location.get("latitude"),
                self.context.location.get("longitude")
            )
        response_text = """🚨 **THIS IS A MEDICAL EMERGENCY** 🚨

> **"This is a medical emergency. Please go to the nearest emergency hospital or call emergency services immediately."**

---

"""
        
        # 1️⃣ Poison Identification (if available)
        if poison_info and not poison_info.get("error"):
            risk_level = self._determine_risk_level(poison_info, severity_result)
            response_text += f"""### 1️⃣ Poison Identification

* **Poison Name:** {poison_info.get('name', 'Unknown')}
* **Category:** {poison_info.get('category', 'Unknown')}
* **Common Sources:** {', '.join(poison_info.get('common_sources', ['Unknown'])[:3])}
* **Risk Level:** {risk_level}

---

"""
        
        # 2️⃣ Symptoms Overview (if available)
        if poison_info:
            immediate_symptoms = poison_info.get('symptoms_immediate', [])
            delayed_symptoms = poison_info.get('symptoms_delayed', [])
            if immediate_symptoms or delayed_symptoms:
                response_text += """### 2️⃣ Symptoms Overview

"""
                if immediate_symptoms:
                    response_text += f"* **Early/Immediate Symptoms:** {', '.join(immediate_symptoms[:5])}\n"
                if delayed_symptoms:
                    response_text += f"* **Severe/Delayed Symptoms:** {', '.join(delayed_symptoms[:5])}\n"
                response_text += "\n*(This is informational only, not a diagnosis)*\n\n---\n\n"
        
        # 3️⃣ Antidote Information (Informational Only)
        if antidote_info:
            response_text += """### 3️⃣ Antidote Information (Informational Only)

"""
            if isinstance(antidote_info, dict):
                if antidote_info.get("primary"):
                    response_text += f"* **Antidote Available:** Yes\n"
                    response_text += f"* **Antidote Name:** {antidote_info.get('primary')}\n"
                else:
                    response_text += f"* **Antidote Information:** {antidote_info}\n"
            else:
                response_text += f"* **Antidote:** {antidote_info}\n"
            
            response_text += """\n> ⚠️ **"Antidotes must only be administered by trained medical professionals."**

---

"""
        
        # 4️⃣ Emergency Action Guidance
        response_text += """### 4️⃣ Emergency Action Guidance

* 📞 **CALL 102 IMMEDIATELY** - Emergency Services
* 📞 **Poison Control:** +977-1-4412505 (NPIC-TUTH)
* 📞 **Toll-Free:** 1102

**IMPORTANT SAFETY INSTRUCTIONS:**
* ❌ Do **NOT** induce vomiting unless specifically instructed by poison control
* ❌ Do **NOT** give any food or drink unless advised by professionals
* ❌ Avoid any unsafe actions or home remedies
* ✅ If unconscious, place person in recovery position
* ✅ If not breathing, call for help and start CPR if trained
* ✅ Bring the poison container/label to the hospital if possible

*(No medical treatment steps provided - seek professional help)*

---

"""
        
        # 5️⃣ Nearest Medical Support
        response_text += "### 5️⃣ Nearest Medical Support\n\n"
        if hospitals:
            response_text += "**🏥 Nearest Hospitals:**\n"
            for h in hospitals[:3]:
                name = h.get('name', 'Unknown')
                phone = h.get('phone', 'N/A')
                address = h.get('address', '')
                response_text += f"* **{name}** - 📞 {phone}\n"
                if address:
                    response_text += f"  * Address: {address}\n"
        else:
            response_text += "* Please share your location to find nearest hospitals\n"
        
        response_text += "\n"
        
        if poison_centers:
            response_text += "**☎️ Nearest Poison Treatment Centers:**\n"
            for c in poison_centers[:2]:
                name = c.get('name', 'Unknown')
                phone = c.get('phone', c.get('toll_free', 'N/A'))
                response_text += f"* **{name}** - 📞 {phone}\n"
        else:
            response_text += "**☎️ Poison Control Center:**\n"
            response_text += "* **Nepal Poison Information Centre (NPIC-TUTH)** - 📞 +977-1-4412505\n"
        
        response_text += '\n> *"This selection is based on proximity and available emergency facilities."*\n\n---\n\n'
        
        # Safe closing line
        response_text += '### ⚠️ IMPORTANT DISCLAIMER\n\n'
        response_text += '> **"This information is for awareness only and does not replace professional medical care. Please seek immediate help from a qualified healthcare provider."**\n\n'
        response_text += '**🚨 DO NOT DELAY - CALL FOR HELP IMMEDIATELY**'
        
        return {
            "message": response_text,
            "is_emergency": True,
            "severity": severity_result["severity"],
            "tools_used": ["assess_severity", "get_emergency_numbers", "get_first_aid", "get_antidote", "find_nearby_hospitals", "find_poison_centers"],
            "emergency_numbers": emergency_numbers,
            "first_aid": first_aid,
            "antidote": antidote_info,
            "nearby_hospitals": hospitals[:3],
            "poison_centers": poison_centers[:2]
        }
    
    def _determine_risk_level(self, poison_info: Dict, severity_result: Dict) -> str:
        """Determine risk level based on poison data and severity assessment"""
        severity = severity_result.get("severity", "").upper()
        
        if severity == "CRITICAL":
            return self.RISK_LEVELS["life_threatening"]
        elif severity == "SEVERE":
            return self.RISK_LEVELS["high"]
        elif severity == "MODERATE":
            return self.RISK_LEVELS["moderate"]
        else:
            return self.RISK_LEVELS["low"]
    
    # Common greetings and non-poison-related phrases to ignore
    GREETING_PATTERNS = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "whats up", "howdy", "greetings",
        "thanks", "thank you", "bye", "goodbye", "ok", "okay", "yes", "no",
        "namaste", "namaskar", "dhanyabad"
    ]
    
    def _is_greeting_or_generic(self, message: str) -> bool:
        """Check if message is a greeting or generic non-poison-related message"""
        message_lower = message.lower().strip()
        
        # Quick action keywords that should NOT be treated as greetings
        quick_action_keywords = [
            "swallowed", "ingestion", "ingested", "ate", "drank", "bite", "emergency",
            "poison", "overdose", "exposure", "chemical", "burn", "hospital", "help",
            "cleaning", "medicine", "plant", "mushroom", "snake", "pesticide", "drug",
            "child", "baby", "toddler", "kid"
        ]
        
        # If message contains any quick action keyword, it's NOT a greeting
        if any(keyword in message_lower for keyword in quick_action_keywords):
            return False
        
        # Check if it's a short greeting
        if len(message_lower) < 20:
            for greeting in self.GREETING_PATTERNS:
                if greeting in message_lower or message_lower in greeting:
                    return True
        
        # Check if message has no meaningful poison-related content
        # (very short messages with no symptoms, no poison keywords)
        words = message_lower.split()
        if len(words) <= 3:
            # Short message - check if it contains any poison-related terms
            has_poison_keyword = self._identify_poison_from_message(message) is not None
            has_symptoms = len(self._extract_symptoms(message)) > 0
            has_emergency = self._is_emergency(message)
            
            if not has_poison_keyword and not has_symptoms and not has_emergency:
                return True
        
        return False
    
    def _analyze_intent(self, message: str) -> Dict:
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        # First check if this is a greeting or generic message
        if self._is_greeting_or_generic(message):
            return {
                "primary": "greeting",
                "secondary": [],
                "entities": {
                    "poison": None,
                    "symptoms": [],
                    "location_requested": False,
                    "treatment_requested": False,
                    "first_aid_requested": False,
                    "information_requested": False
                }
            }
        
        intent = {
            "primary": None,
            "secondary": [],
            "entities": {
                "poison": self._identify_poison_from_message(message),
                "symptoms": self._extract_symptoms(message),
                "location_requested": any(w in message_lower for w in ["hospital", "center", "nearby", "closest", "where", "find"]),
                "treatment_requested": any(w in message_lower for w in ["treatment", "antidote", "cure", "medicine", "protocol", "manage"]),
                "first_aid_requested": any(w in message_lower for w in ["first aid", "what to do", "help", "immediately", "should i do"]),
                "information_requested": any(w in message_lower for w in ["what is", "tell me about", "information", "symptoms of", "about", "know"]),
                "lab_testing_requested": any(w in message_lower for w in ["lab", "test", "blood test", "drug screen", "screening", "cbc", "diagnostic", "urine test", "toxicology test"])
            }
        }
        
        # Determine primary intent
        if intent["entities"]["lab_testing_requested"]:
            intent["primary"] = "find_labs"
        elif intent["entities"]["symptoms"]:
            intent["primary"] = "symptom_analysis"
        elif intent["entities"]["poison"]:
            # If poison is mentioned, default to getting info about it
            if intent["entities"]["treatment_requested"]:
                intent["primary"] = "treatment_info"
            elif intent["entities"]["first_aid_requested"]:
                intent["primary"] = "first_aid"
            else:
                intent["primary"] = "poison_info"
                intent["entities"]["information_requested"] = True
        elif intent["entities"]["treatment_requested"]:
            intent["primary"] = "treatment_info"
        elif intent["entities"]["first_aid_requested"]:
            intent["primary"] = "first_aid"
        elif intent["entities"]["location_requested"]:
            intent["primary"] = "find_help"
        elif intent["entities"]["information_requested"]:
            intent["primary"] = "general_inquiry"
        else:
            # No clear intent - treat as general inquiry, NOT symptom analysis
            # This prevents false positives from random words being treated as symptoms
            intent["primary"] = "general_inquiry"
        
        return intent
    
    async def _execute_plan(self, intent: Dict, message: str) -> List[ToolResult]:
        """Execute tools based on analyzed intent"""
        results = []
        
        # If it's a greeting or general inquiry with no specific content, don't run any tools
        if intent["primary"] == "greeting" or intent["primary"] == "general_inquiry":
            # Only get emergency numbers for reference
            result = self.tools["get_emergency_numbers"].execute()
            results.append(result)
            return results
        
        # Handle lab testing requests
        if intent["primary"] == "find_lab" or intent["entities"].get("lab_testing_requested"):
            lat = self.context.location.get("latitude") if self.context.location else None
            lon = self.context.location.get("longitude") if self.context.location else None
            
            # Determine test type from message - use None to get all labs,
            # then filter/highlight based on drug screening capability
            message_lower = message.lower()
            test_type = None  # Get all labs first
            require_toxicology = False
            
            # Flag for drug screening specific request
            if "drug" in message_lower or "urine" in message_lower or "screen" in message_lower:
                require_toxicology = True
            elif "toxicology" in message_lower or "heavy metal" in message_lower:
                require_toxicology = True
            
            lab_result = self._tool_find_diagnostic_labs(latitude=lat, longitude=lon, test_type=test_type)
            results.append(ToolResult(
                tool_name="find_diagnostic_labs",
                success=True,
                data=lab_result
            ))
            self.context.tools_used.append("find_diagnostic_labs")
            
            # Also get emergency numbers
            result = self.tools["get_emergency_numbers"].execute()
            results.append(result)
            return results
        
        # Analyze symptoms only if we have actual symptoms identified
        if intent["entities"]["symptoms"] and intent["primary"] == "symptom_analysis":
            symptoms = " ".join(intent["entities"]["symptoms"])
            result = self.tools["analyze_symptoms"].execute(symptoms=symptoms)
            results.append(result)
            self.context.tools_used.append("analyze_symptoms")
        
        # Get poison info if identified
        poison = intent["entities"]["poison"] or self.context.identified_poison
        if poison:
            if intent["entities"]["treatment_requested"] or intent["primary"] == "treatment_info":
                # Get full protocol
                result = self.tools["get_management_protocol"].execute(poison_name=poison)
                results.append(result)
                
                result = self.tools["get_antidote"].execute(poison_name=poison)
                results.append(result)
                self.context.tools_used.extend(["get_management_protocol", "get_antidote"])
            
            if intent["entities"]["first_aid_requested"] or intent["primary"] == "first_aid":
                result = self.tools["get_first_aid"].execute(poison_name=poison)
                results.append(result)
                self.context.tools_used.append("get_first_aid")
            
            if intent["primary"] == "poison_info" or intent["entities"]["information_requested"]:
                result = self.tools["get_poison_info"].execute(poison_name=poison)
                results.append(result)
                self.context.tools_used.append("get_poison_info")
        
        # Find nearby help if requested
        if intent["entities"]["location_requested"]:
            lat = self.context.location.get("latitude") if self.context.location else None
            lon = self.context.location.get("longitude") if self.context.location else None
            
            result = self.tools["find_nearby_hospitals"].execute(latitude=lat, longitude=lon)
            results.append(result)
            
            result = self.tools["find_poison_centers"].execute(latitude=lat, longitude=lon)
            results.append(result)
            self.context.tools_used.extend(["find_nearby_hospitals", "find_poison_centers"])
        
        # Always get emergency numbers
        result = self.tools["get_emergency_numbers"].execute()
        results.append(result)
        
        return results
    
    def _generate_structured_response(
        self,
        poison_info: Dict,
        hospitals_data: List[Dict],
        centers_data: List[Dict],
        severity_result: Dict = None
    ) -> str:
        """
        Generate response following the STRICT 6-section template:
        
        1️⃣ Summary
        2️⃣ Symptoms
        3️⃣ Antidote Availability (name only, NO dosage)
        4️⃣ What to do now
        5️⃣ Nearby facilities (best + nearest)
        6️⃣ Disclaimer
        """
        response_parts = []
        
        # 1️⃣ SUMMARY
        response_parts.append("### 1️⃣ Summary")
        poison_name = poison_info.get("name", "Unknown substance")
        category = poison_info.get("category", "Unknown")
        risk_level = self._determine_risk_level(poison_info, severity_result or {})
        
        response_parts.append(f"**{poison_name}** is a **{category}** poison.")
        common_sources = poison_info.get("common_sources", [])
        if common_sources:
            response_parts.append(f"**Common sources:** {', '.join(common_sources[:3])}")
        response_parts.append(f"**Risk Level:** {risk_level}")
        response_parts.append("")
        
        # 2️⃣ SYMPTOMS
        response_parts.append("### 2️⃣ Symptoms")
        immediate_symptoms = poison_info.get("symptoms_immediate", [])
        delayed_symptoms = poison_info.get("symptoms_delayed", [])
        
        if immediate_symptoms:
            response_parts.append(f"**Early symptoms:** {', '.join(immediate_symptoms[:5])}")
        if delayed_symptoms:
            response_parts.append(f"**Danger signs (seek help immediately):** {', '.join(delayed_symptoms[:5])}")
        if not immediate_symptoms and not delayed_symptoms:
            response_parts.append("*Symptom information not available for this substance.*")
        response_parts.append("")
        response_parts.append("*(This is informational only, not a diagnosis)*")
        response_parts.append("")
        
        # 3️⃣ ANTIDOTE AVAILABILITY (name only, NO dosage)
        response_parts.append("### 3️⃣ Antidote Information")
        antidote = poison_info.get("antidote")
        
        if antidote:
            if isinstance(antidote, dict):
                antidote_name = antidote.get("primary", antidote.get("name", "Available"))
                response_parts.append(f"**Antidote exists:** Yes")
                response_parts.append(f"**Antidote name:** {antidote_name}")
            else:
                response_parts.append(f"**Antidote exists:** Yes")
                response_parts.append(f"**Antidote name:** {antidote}")
        else:
            response_parts.append("**Antidote exists:** No specific antidote / Supportive care needed")
        
        response_parts.append("")
        response_parts.append("> ⚠️ **\"Antidotes must only be administered by trained medical professionals.\"**")
        response_parts.append("")
        
        # 4️⃣ WHAT TO DO NOW
        response_parts.append("### 4️⃣ What To Do Now")
        do_not_do = poison_info.get("do_not_do", [])
        
        response_parts.append("**✅ DO:**")
        response_parts.append("- Call Poison Control immediately: **+977-1-4412505**")
        response_parts.append("- Go to the nearest hospital emergency department")
        response_parts.append("- Bring the container/label of the substance if possible")
        response_parts.append("- Note the time of exposure and estimated amount")
        response_parts.append("")
        
        response_parts.append("**❌ DO NOT:**")
        if do_not_do:
            for item in do_not_do[:4]:
                response_parts.append(f"- {item}")
        else:
            response_parts.append("- Do NOT induce vomiting unless told by poison control")
            response_parts.append("- Do NOT give any food or drink unless advised")
            response_parts.append("- Do NOT try home remedies")
        response_parts.append("")
        
        # 5️⃣ NEARBY FACILITIES (Best + Nearest)
        response_parts.append("### 5️⃣ Nearest Medical Support")
        
        if hospitals_data:
            response_parts.append("**🏥 Recommended Hospitals** (ranked by poison care capability + proximity):")
            for i, h in enumerate(hospitals_data[:3], 1):
                name = h.get("name", "Unknown")
                phone = h.get("phone", "N/A")
                address = h.get("address", "")
                suitability = h.get("suitability_score", 0)
                
                # Mark best choice
                if i == 1:
                    response_parts.append(f"- **⭐ {name}** (Best choice) - 📞 {phone}")
                else:
                    response_parts.append(f"- **{name}** - 📞 {phone}")
                if address:
                    response_parts.append(f"  📍 {address}")
        else:
            response_parts.append("*Please share your location to find nearest hospitals.*")
        
        response_parts.append("")
        
        if centers_data:
            response_parts.append("**☎️ Poison Control Centers:**")
            for c in centers_data[:2]:
                name = c.get("name", "Unknown")
                phone = c.get("phone", c.get("toll_free", "N/A"))
                response_parts.append(f"- **{name}** - 📞 {phone}")
        else:
            response_parts.append("**☎️ Poison Control:**")
            response_parts.append("- **Nepal Poison Information Centre (NPIC-TUTH)** - 📞 +977-1-4412505")
        
        response_parts.append("")
        response_parts.append("> *Selection based on proximity + poison case readiness.*")
        response_parts.append("")
        
        # 6️⃣ DISCLAIMER
        response_parts.append("---")
        response_parts.append("### ⚠️ Important Disclaimer")
        response_parts.append("")
        response_parts.append("> **\"This information is for awareness only and does not replace professional medical care.\"**")
        response_parts.append("")
        response_parts.append("🚨 **Emergency:** Call **102** | Poison Control: **+977-1-4412505** | Toll-Free: **1102**")
        
        return "\n".join(response_parts)

    def _synthesize_response(self, intent: Dict, tool_results: List[ToolResult], original_message: str) -> Dict:
        """
        Synthesize final response from tool results
        
        Response Structure (FOLLOW STRICTLY):
        1️⃣ Poison Identification
        2️⃣ Symptoms Overview
        3️⃣ Antidote Information (Informational Only)
        4️⃣ Emergency Action Guidance
        5️⃣ Nearest Medical Support (Location-Based)
        """
        response_parts = []
        response_data = {
            "is_emergency": False,
            "tools_used": self.context.tools_used[-10:],
            "identified_poison": None,
            "confidence": None,
            "risk_level": None,
            "symptoms": None,
            "antidote": None,
            "nearby_hospitals": [],
            "poison_centers": [],
            "emergency_numbers": {}
        }
        
        # Collect data from tool results
        poison_info = None
        symptoms_data = None
        antidote_data = None
        first_aid_data = None
        hospitals_data = []
        centers_data = []
        emergency_numbers = {}
        ml_prediction = None
        
        for result in tool_results:
            if not result.success:
                continue
            
            if result.tool_name == "analyze_symptoms":
                ml_prediction = result.data.get("ml_prediction", {})
                symptoms_data = result.data
            elif result.tool_name == "get_poison_info":
                poison_info = result.data
            elif result.tool_name == "get_antidote":
                antidote_data = result.data.get("antidote")
            elif result.tool_name == "get_first_aid":
                first_aid_data = result.data.get("first_aid_steps")
            elif result.tool_name == "find_nearby_hospitals":
                hospitals_data = result.data or []
            elif result.tool_name == "find_poison_centers":
                centers_data = result.data or []
            elif result.tool_name == "get_emergency_numbers":
                emergency_numbers = result.data or {}
            elif result.tool_name == "get_management_protocol":
                # Protocol info for medical professionals only
                pass
        
        response_data["emergency_numbers"] = emergency_numbers
        response_data["nearby_hospitals"] = hospitals_data[:5]
        response_data["poison_centers"] = centers_data[:3]
        
        # Check if we have useful content
        has_poison_info = poison_info and not poison_info.get("error")
        has_prediction = ml_prediction and ml_prediction.get("primary_prediction")
        
        # Handle different types of responses conversationally
        
        # GREETING or GENERAL INQUIRY - respond naturally
        if intent["primary"] == "greeting":
            greetings = [
                "Hello! 👋 I'm PoisonSense AI, your friendly assistant for poison information and emergency guidance.",
                "",
                "I can help you with:",
                "- 🧪 Information about various poisons and toxic substances",
                "- 💊 Antidote information (for awareness, not treatment)",
                "- 🩺 Symptom identification and risk assessment", 
                "- 🏥 Finding nearby hospitals and poison control centers",
                "- 🚨 Emergency guidance for poisoning cases",
                "",
                "**How can I assist you today?**",
                "",
                "Feel free to ask me anything like:",
                '- "What are the symptoms of paracetamol overdose?"',
                '- "Tell me about snake bite treatment"',
                '- "Find nearest hospital"',
                "",
                "---",
                "⚠️ *If this is an emergency, please call **102** immediately!*"
            ]
            response_data["message"] = "\n".join(greetings)
            return response_data
        
        # GENERAL INQUIRY with no specific poison context
        if intent["primary"] == "general_inquiry" and not has_poison_info and not has_prediction:
            response_parts.append("I'd be happy to help! 😊")
            response_parts.append("")
            response_parts.append("Could you tell me more about what you'd like to know? For example:")
            response_parts.append("- **Specific poison information** - Ask about paracetamol, pesticides, snake bites, etc.")
            response_parts.append("- **Symptoms you're observing** - Describe what symptoms someone is experiencing")
            response_parts.append("- **Emergency guidance** - If someone has been exposed to a toxic substance")
            response_parts.append("- **Find help** - Locate nearby hospitals or poison control centers")
            response_parts.append("")
            response_parts.append("Just let me know what you need! 💬")
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("🚨 *Emergency? Call **102** | Poison Control: **+977-1-4412505***")
            
            response_data["message"] = "\n".join(response_parts)
            return response_data
        
        # LAB TESTING REQUEST - show diagnostic labs with test capabilities
        if intent["primary"] == "find_lab" or intent["entities"].get("lab_testing_requested"):
            labs_data = []
            drug_labs_data = []
            testing_guidance = None
            
            # Extract lab data from tool results
            for result in tool_results:
                if result.success and result.tool_name == "find_diagnostic_labs":
                    lab_result = result.data or {}
                    labs_data = lab_result.get("labs", [])
                    drug_labs_data = lab_result.get("drug_screening_labs", [])
                    testing_guidance = lab_result.get("testing_guidance")
                    break
            
            if labs_data or drug_labs_data:
                response_parts.append("## 🔬 Diagnostic Labs for Toxicology Testing")
                response_parts.append("")
                response_parts.append("Here are the diagnostic laboratories where you can get toxicology-related tests in the Kathmandu area:")
                response_parts.append("")
                
                # Combine and use labs from both sources, prefer drug_labs for drug screening queries
                all_labs = labs_data if labs_data else []
                
                for i, lab in enumerate(all_labs[:6], 1):
                    name = lab.get("facility_name", "Unknown Lab")
                    address = lab.get("address", "Address not available")
                    phone = lab.get("phone_primary", "N/A")
                    notes = lab.get("notes", "")
                    tests = lab.get("lab_tests_available", [])
                    has_tox = lab.get("has_toxicology", False)
                    
                    response_parts.append(f"### {i}. {name}")
                    response_parts.append(f"📍 **Address:** {address}")
                    response_parts.append(f"📞 **Phone:** {phone}")
                    if has_tox:
                        response_parts.append("✅ **Toxicology Testing Available**")
                    
                    if tests:
                        tests_str = ", ".join(tests[:5])
                        if len(tests) > 5:
                            tests_str += f" (+{len(tests)-5} more)"
                        response_parts.append(f"🧪 **Tests Available:** {tests_str}")
                    
                    if notes:
                        response_parts.append(f"📝 *{notes}*")
                    response_parts.append("")
                
                response_parts.append("---")
                response_parts.append("### 📋 Important Notes:")
                response_parts.append("- **Bring a doctor's referral** if you have one for better interpretation of results")
                response_parts.append("- **Fasting may be required** for some tests - call ahead to confirm")
                response_parts.append("- **Bring valid ID** for sample collection")
                response_parts.append("- Results typically take **24-72 hours** depending on the test")
                response_parts.append("")
                response_parts.append("---")
                response_parts.append("⚠️ *If this is related to a poisoning emergency, please call **102** or go to the nearest hospital emergency department immediately.*")
                
                response_data["message"] = "\n".join(response_parts)
                response_data["diagnostic_labs"] = all_labs[:6]
                return response_data
            else:
                # No labs found - give general guidance
                response_parts.append("## 🔬 Toxicology Testing Information")
                response_parts.append("")
                response_parts.append("For toxicology and drug screening tests, you can visit any major diagnostic laboratory in Kathmandu.")
                response_parts.append("")
                response_parts.append("### Common Toxicology Tests Available:")
                response_parts.append("- **Urine Drug Screen** (6-drug or 9-drug panel)")
                response_parts.append("- **Blood Drug Levels** (for specific medications)")
                response_parts.append("- **Cholinesterase Testing** (organophosphate/carbamate exposure)")
                response_parts.append("- **Heavy Metal Testing** (lead, mercury, arsenic)")
                response_parts.append("")
                response_parts.append("### Recommended Labs:")
                response_parts.append("- **National Reference Laboratory** - Teku, +977-1-4261807")
                response_parts.append("- **Nepal Lab House** - Kathmandu, +977-1-4252077")
                response_parts.append("- **NITA Polyclinic** - Lazimpat, +977-1-4443802")
                response_parts.append("")
                response_parts.append("---")
                response_parts.append("📍 *Share your location for more personalized recommendations.*")
                
                response_data["message"] = "\n".join(response_parts)
                return response_data
        
        # POISON INFORMATION REQUEST - Use strict 6-section template
        if has_poison_info or has_prediction:
            # Get poison details
            if has_prediction:
                pred = ml_prediction["primary_prediction"]
                poison_name = pred.get("poison_name", "Unknown")
                confidence = pred.get("confidence", 0)
                
                response_data["identified_poison"] = poison_name
                response_data["confidence"] = confidence
                self.context.identified_poison = poison_name
                
                if not has_poison_info and poison_name:
                    poison_id = self._normalize_poison_name(poison_name)
                    poison_info = get_poison_details(poison_id)
                    has_poison_info = poison_info and not poison_info.get("error")
            
            if has_poison_info:
                # Determine risk level
                severity_result = self._tool_assess_severity(original_message, poison_info.get("name", ""))
                
                # Update response data
                response_data["risk_level"] = self._determine_risk_level(poison_info, severity_result)
                response_data["symptoms"] = {
                    "immediate": poison_info.get("symptoms_immediate", []),
                    "delayed": poison_info.get("symptoms_delayed", [])
                }
                response_data["antidote"] = poison_info.get("antidote")
                
                # Generate response using STRICT 6-section template
                structured_response = self._generate_structured_response(
                    poison_info=poison_info,
                    hospitals_data=hospitals_data,
                    centers_data=centers_data,
                    severity_result=severity_result
                )
                
                response_data["message"] = structured_response
                return response_data
            else:
                # Prediction but no detailed info - still provide structured help
                response_parts.append(f"Based on your description, this might be related to **{poison_name}** poisoning.")
                response_parts.append("")
                response_parts.append("I don't have detailed information about this specific substance in my database.")
                response_parts.append("")
                response_parts.append("### What You Should Do:")
                response_parts.append("1. **Call Poison Control immediately:** +977-1-4412505")
                response_parts.append("2. **Go to the nearest hospital** emergency department")
                response_parts.append("3. **Bring the container/label** if available")
                response_parts.append("")
                response_parts.append("---")
                response_parts.append("> *This information is for awareness only. Please seek professional medical care.*")
                
                response_data["message"] = "\n".join(response_parts)
                return response_data
        
        # LOCATION REQUEST - include hospital info
        if intent["entities"]["location_requested"] or hospitals_data or centers_data:
            response_parts.append("## 🏥 Nearby Medical Help")
            
            if hospitals_data:
                response_parts.append("**Hospitals:**")
                for h in hospitals_data[:3]:
                    name = h.get("name", "Unknown")
                    phone = h.get("phone", "N/A")
                    address = h.get("address", "")
                    response_parts.append(f"- **{name}** - 📞 {phone}")
                    if address:
                        response_parts.append(f"  📍 {address}")
                response_parts.append("")
            
            if centers_data:
                response_parts.append("**Poison Control Centers:**")
                for c in centers_data[:2]:
                    name = c.get("name", "Unknown")
                    phone = c.get("phone", c.get("toll_free", "N/A"))
                    response_parts.append(f"- **{name}** - 📞 {phone}")
                response_parts.append("")
            elif not hospitals_data:
                response_parts.append("Share your location and I can help find the nearest hospitals!")
                response_parts.append("")
        
        # Add emergency footer for poison-related queries
        if has_poison_info or has_prediction or intent["entities"]["symptoms"]:
            response_parts.append("---")
            response_parts.append("🚨 **Emergency Contacts:** Call **102** | Poison Control: **+977-1-4412505** | Toll-Free: **1102**")
            response_parts.append("")
            response_parts.append("*This information is for awareness only. Please seek professional medical care.*")
        
        # Fallback if we still have no content
        if not response_parts:
            response_parts.append("I'm here to help! Could you please tell me more about what you'd like to know?")
            response_parts.append("")
            response_parts.append("You can ask me about:")
            response_parts.append("- Poison information and symptoms")
            response_parts.append("- Emergency guidance")
            response_parts.append("- Finding nearby hospitals")
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("🚨 *If this is an emergency, call **102** immediately!*")
        
        response_data["message"] = "\n".join(response_parts)
        
        return response_data
    
    def reset_context(self):
        """Reset conversation context"""
        self.context = ConversationContext()
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation"""
        return {
            "messages_count": len(self.context.messages),
            "identified_poison": self.context.identified_poison,
            "severity_level": self.context.severity_level,
            "symptoms_reported": list(set(self.context.symptoms_reported)),
            "tools_used": list(set(self.context.tools_used)),
            "recommendations_given": self.context.recommendations_given
        }


# Factory function to create agent
def create_agent(db: Session) -> PoisonSenseAgent:
    """Create a new PoisonSense agent instance"""
    return PoisonSenseAgent(db)
