# Agentic AI Service - PoisonSense AI Agent with Tools
"""
This module implements an Agentic AI system for poison information.
The agent has access to tools for:
- Searching poison database
- Finding antidotes
- Locating hospitals
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
    2. Provide first aid instructions
    3. Look up antidotes and dosages
    4. Find nearby hospitals and poison centers
    5. Provide comprehensive treatment protocols
    6. Maintain conversation context
    7. Escalate emergencies appropriately
    """
    
    SYSTEM_PROMPT = """You are PoisonSense AI, an expert toxicology assistant designed to help in poison emergencies.

Your capabilities:
1. ANALYZE symptoms to identify possible poisoning
2. PROVIDE immediate first aid instructions  
3. LOOK UP antidotes, dosages, and treatment protocols
4. FIND nearby hospitals and poison control centers
5. GUIDE users through emergency response

CRITICAL RULES:
- Always prioritize life-threatening symptoms
- Always recommend calling emergency services (102 in Nepal) for serious cases
- Never delay critical advice for additional questions
- Always include emergency numbers in responses
- Be clear about the urgency level
- Cite medical sources when providing treatment information

You have access to:
- Comprehensive poison database with real medical data
- ML model for symptom analysis
- Hospital and poison center locations
- Treatment protocols from WHO, CDC, and NPIC guidelines
"""

    EMERGENCY_KEYWORDS = [
        "unconscious", "not breathing", "seizure", "cardiac arrest",
        "difficulty breathing", "blue lips", "turning blue", "cyanosis",
        "no pulse", "collapse", "unresponsive", "dying", "critical"
    ]
    
    POISON_KEYWORDS = {
        "organophosphate": ["pesticide", "insecticide", "malathion", "parathion", "farm spray", "bug spray"],
        "acetaminophen": ["paracetamol", "tylenol", "crocin", "panadol", "fever medicine"],
        "opioid": ["morphine", "heroin", "fentanyl", "oxycodone", "codeine", "tramadol", "brown sugar"],
        "snake": ["snake bite", "cobra", "krait", "viper", "serpent"],
        "methanol": ["wood alcohol", "spurious liquor", "hooch", "local alcohol"],
        "rat_poison": ["rat poison", "rodenticide", "ratol", "mouse poison"],
        "kerosene": ["kerosene", "petrol", "diesel", "fuel", "paraffin"],
        "corrosive": ["acid", "alkali", "toilet cleaner", "drain cleaner", "bleach"],
        "oleander": ["oleander", "kaner", "yellow flower plant"],
        "mushroom": ["mushroom", "wild mushroom", "toadstool"],
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
        }
    
    # ==========================================================================
    # TOOL IMPLEMENTATIONS
    # ==========================================================================
    
    def _tool_analyze_symptoms(self, symptoms: str) -> Dict:
        """Analyze symptoms using ML and database"""
        # First, try ML model
        ml_result = ml_service.predict(symptoms)
        
        # Also search database
        symptom_list = [s.strip() for s in symptoms.replace(',', ' ').split() if len(s.strip()) > 2]
        db_matches = get_poison_by_symptoms(symptom_list)
        
        # Combine results
        combined = {
            "ml_prediction": ml_result,
            "database_matches": db_matches[:5],
            "confidence_assessment": self._assess_prediction_confidence(ml_result, db_matches)
        }
        
        # Update context
        self.context.symptoms_reported.extend(symptom_list)
        if ml_result.get("primary_prediction"):
            self.context.identified_poison = ml_result["primary_prediction"].get("poison_name")
        
        return combined
    
    def _tool_get_poison_info(self, poison_name: str) -> Dict:
        """Get comprehensive poison information"""
        # Normalize poison name
        poison_id = self._normalize_poison_name(poison_name)
        
        # Get from comprehensive database
        poison_data = get_poison_details(poison_id)
        
        if not poison_data:
            # Try database
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
        """Find nearby hospitals"""
        if latitude and longitude:
            hospitals = self.location_service.find_nearby_hospitals(
                latitude, longitude, radius_km=50, limit=10, antidote_name=antidote
            )
        else:
            # Return Kathmandu hospitals as default
            hospitals = self.db.query(Hospital).filter(
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
                } for h in hospitals
            ]
        
        return hospitals
    
    def _tool_find_poison_centers(self, latitude: float = None, longitude: float = None) -> List[Dict]:
        """Find nearby poison control centers"""
        if latitude and longitude:
            centers = self.location_service.find_nearby_poison_centers(
                latitude, longitude, radius_km=100, limit=5
            )
        else:
            # Return all Nepal centers
            centers = self.db.query(PoisonCenter).filter(
                PoisonCenter.country == "Nepal"
            ).all()
            
            centers = [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone_primary,
                    "toll_free": c.toll_free_number,
                    "address": f"{c.address}, {c.city}",
                    "is_24_hours": c.is_24_hours
                } for c in centers
            ]
        
        return centers
    
    def _tool_get_emergency_numbers(self, country: str = "nepal") -> Dict:
        """Get emergency numbers"""
        return EMERGENCY_NUMBERS.get(country.lower(), EMERGENCY_NUMBERS["nepal"])
    
    def _tool_assess_severity(self, symptoms: str, poison_name: str = None) -> Dict:
        """Assess severity of poisoning"""
        symptoms_lower = symptoms.lower()
        
        # Check for critical symptoms
        critical_symptoms = [
            "not breathing", "unconscious", "seizure", "cardiac arrest",
            "no pulse", "cyanosis", "respiratory failure", "coma"
        ]
        
        severe_symptoms = [
            "difficulty breathing", "vomiting blood", "severe pain",
            "paralysis", "collapse", "blood pressure drop", "arrhythmia"
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
        """Check if message indicates emergency"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.EMERGENCY_KEYWORDS)
    
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
        1. Understand intent
        2. Determine which tools to use
        3. Execute tools
        4. Synthesize response
        5. Update context
        """
        # Store location
        if latitude and longitude:
            self.context.location = {"latitude": latitude, "longitude": longitude}
        
        # Add user message to context
        self.context.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        
        # Check for emergency first
        if self._is_emergency(user_message):
            return await self._handle_emergency(user_message)
        
        # Identify intent and plan actions
        intent = self._analyze_intent(user_message)
        
        # Execute planned actions
        tool_results = await self._execute_plan(intent, user_message)
        
        # Generate response
        response = self._synthesize_response(intent, tool_results, user_message)
        
        # Add assistant response to context
        self.context.messages.append(ConversationMessage(
            role="assistant",
            content=response["message"]
        ))
        
        return response
    
    async def _handle_emergency(self, message: str) -> Dict:
        """Handle emergency situations with immediate response"""
        severity_result = self._tool_assess_severity(message)
        emergency_numbers = self._tool_get_emergency_numbers()
        
        # Get first aid if poison identified
        poison_id = self._identify_poison_from_message(message)
        first_aid = None
        if poison_id:
            first_aid_result = self._tool_get_first_aid(poison_id)
            first_aid = first_aid_result.get("first_aid_steps")
        
        # Find nearby hospitals
        hospitals = []
        if self.context.location:
            hospitals = self._tool_find_nearby_hospitals(
                self.context.location.get("latitude"),
                self.context.location.get("longitude")
            )
        
        response_text = f"""🚨 **EMERGENCY DETECTED** 🚨

**Severity Level:** {severity_result['severity']}

**IMMEDIATE ACTIONS:**
1. 📞 **CALL 102 NOW** - Emergency Services
2. 📞 **Poison Control:** +977-1-4412505 (NPIC-TUTH)
3. 📞 **Toll-Free:** 1102

"""
        
        if first_aid:
            response_text += "**FIRST AID STEPS:**\n"
            for i, step in enumerate(first_aid[:5], 1):
                response_text += f"{i}. {step}\n"
            response_text += "\n"
        else:
            response_text += """**GENERAL FIRST AID:**
1. Remove person from exposure source
2. If not breathing, start CPR
3. If unconscious, place in recovery position
4. Do NOT induce vomiting unless told by poison control
5. Keep the substance container for identification

"""
        
        if hospitals:
            response_text += "**NEAREST HOSPITALS:**\n"
            for h in hospitals[:3]:
                response_text += f"• {h.get('name')}: 📞 {h.get('phone', 'N/A')}\n"
        
        response_text += "\n⚠️ **DO NOT DELAY - CALL FOR HELP IMMEDIATELY**"
        
        return {
            "message": response_text,
            "is_emergency": True,
            "severity": severity_result["severity"],
            "tools_used": ["assess_severity", "get_emergency_numbers", "get_first_aid", "find_nearby_hospitals"],
            "emergency_numbers": emergency_numbers,
            "first_aid": first_aid,
            "nearby_hospitals": hospitals[:3]
        }
    
    def _analyze_intent(self, message: str) -> Dict:
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        intent = {
            "primary": None,
            "secondary": [],
            "entities": {
                "poison": self._identify_poison_from_message(message),
                "symptoms": self._extract_symptoms(message),
                "location_requested": any(w in message_lower for w in ["hospital", "center", "nearby", "closest", "where", "find"]),
                "treatment_requested": any(w in message_lower for w in ["treatment", "antidote", "cure", "medicine", "protocol", "manage"]),
                "first_aid_requested": any(w in message_lower for w in ["first aid", "what to do", "help", "immediately", "should i do"]),
                "information_requested": any(w in message_lower for w in ["what is", "tell me about", "information", "symptoms of", "about", "know"])
            }
        }
        
        # Determine primary intent
        if intent["entities"]["symptoms"]:
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
            # Default: try to analyze as symptoms
            intent["primary"] = "symptom_analysis"
            intent["entities"]["symptoms"] = message.split()[:10]  # Use message words as potential symptoms
        
        return intent
    
    async def _execute_plan(self, intent: Dict, message: str) -> List[ToolResult]:
        """Execute tools based on analyzed intent"""
        results = []
        
        # Always analyze symptoms if present
        if intent["entities"]["symptoms"] or intent["primary"] == "symptom_analysis":
            symptoms = " ".join(intent["entities"]["symptoms"]) if intent["entities"]["symptoms"] else message
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
    
    def _synthesize_response(self, intent: Dict, tool_results: List[ToolResult], original_message: str) -> Dict:
        """Synthesize final response from tool results"""
        response_parts = []
        response_data = {
            "is_emergency": False,
            "tools_used": self.context.tools_used[-10:],  # Last 10 tools
            "identified_poison": None,
            "confidence": None,
            "first_aid": None,
            "antidote": None,
            "nearby_hospitals": [],
            "emergency_numbers": {}
        }
        
        has_useful_content = False
        
        # Process each tool result
        for result in tool_results:
            if not result.success:
                continue
            
            if result.tool_name == "analyze_symptoms":
                data = result.data
                if data.get("ml_prediction", {}).get("primary_prediction"):
                    pred = data["ml_prediction"]["primary_prediction"]
                    poison_name = pred.get("poison_name", "Unknown")
                    confidence = pred.get("confidence", 0)
                    
                    response_data["identified_poison"] = poison_name
                    response_data["confidence"] = confidence
                    self.context.identified_poison = poison_name
                    
                    response_parts.append(f"**🔍 AI Analysis Result:**")
                    response_parts.append(f"**Suspected Poisoning:** {poison_name}")
                    response_parts.append(f"**Confidence:** {confidence*100:.1f}%")
                    response_parts.append(f"**Assessment:** {data.get('confidence_assessment', 'N/A')}")
                    response_parts.append("")
                    has_useful_content = True
                    
                    # If we identified a poison, also get its info
                    if poison_name and poison_name != "Unknown":
                        poison_id = poison_name.lower().replace(" ", "_")
                        poison_info = get_poison_details(poison_id)
                        if poison_info and not poison_info.get("error"):
                            if poison_info.get("first_aid"):
                                response_parts.append("**🩹 Recommended First Aid:**")
                                for step in poison_info["first_aid"][:5]:
                                    response_parts.append(f"• {step}")
                                response_parts.append("")
                            if poison_info.get("antidote"):
                                antidote = poison_info["antidote"]
                                response_parts.append(f"**💊 Antidote:** {antidote.get('primary', antidote) if isinstance(antidote, dict) else antidote}")
                                response_parts.append("")
            
            elif result.tool_name == "get_first_aid":
                data = result.data
                if data.get("first_aid_steps"):
                    response_data["first_aid"] = data["first_aid_steps"]
                    response_parts.append("**🩹 First Aid Instructions:**")
                    for step in data["first_aid_steps"][:7]:
                        response_parts.append(f"• {step}")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "get_antidote":
                data = result.data
                if data.get("antidote"):
                    antidote = data["antidote"]
                    response_data["antidote"] = antidote
                    response_parts.append("**💊 Antidote Information:**")
                    if isinstance(antidote, dict):
                        if antidote.get("primary"):
                            response_parts.append(f"**Primary Antidote:** {antidote['primary']}")
                        for key, value in antidote.items():
                            if key != "primary" and isinstance(value, str):
                                response_parts.append(f"• {key}: {value}")
                    else:
                        response_parts.append(f"**Antidote:** {antidote}")
                    response_parts.append("⚠️ *Antidotes should only be administered by medical professionals*")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "get_management_protocol":
                data = result.data
                if data.get("management_protocol"):
                    response_parts.append("**📋 Management Protocol:**")
                    for step in data["management_protocol"][:8]:
                        response_parts.append(f"• {step}")
                    if data.get("contraindications"):
                        response_parts.append("\n**⛔ Contraindications:**")
                        for c in data["contraindications"][:3]:
                            response_parts.append(f"• {c}")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "get_poison_info":
                data = result.data
                if data and not data.get("error"):
                    response_parts.append(f"**📖 Information: {data.get('name', 'Unknown')}**")
                    if data.get("common_names"):
                        response_parts.append(f"**Also known as:** {', '.join(data['common_names'][:5])}")
                    if data.get("category"):
                        response_parts.append(f"**Category:** {data['category']}")
                    if data.get("symptoms_immediate"):
                        response_parts.append(f"**Immediate Symptoms:** {', '.join(data['symptoms_immediate'][:5])}")
                    if data.get("symptoms_delayed"):
                        response_parts.append(f"**Delayed Symptoms:** {', '.join(data['symptoms_delayed'][:5])}")
                    if data.get("antidote"):
                        antidote = data["antidote"]
                        if isinstance(antidote, dict):
                            response_parts.append(f"**Antidote:** {antidote.get('primary', 'See medical professional')}")
                        else:
                            response_parts.append(f"**Antidote:** {antidote}")
                    if data.get("first_aid"):
                        response_parts.append("\n**🩹 First Aid:**")
                        for step in data["first_aid"][:4]:
                            response_parts.append(f"• {step}")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "find_nearby_hospitals":
                data = result.data
                if data:
                    response_data["nearby_hospitals"] = data[:5]
                    response_parts.append("**🏥 Nearby Hospitals:**")
                    for h in data[:3]:
                        name = h.get("name", "Unknown")
                        phone = h.get("phone", "N/A")
                        response_parts.append(f"• **{name}** - 📞 {phone}")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "find_poison_centers":
                data = result.data
                if data:
                    response_parts.append("**☎️ Poison Control Centers:**")
                    for c in data[:2]:
                        name = c.get("name", "Unknown")
                        phone = c.get("phone", c.get("toll_free", "N/A"))
                        response_parts.append(f"• **{name}** - 📞 {phone}")
                    response_parts.append("")
                    has_useful_content = True
            
            elif result.tool_name == "get_emergency_numbers":
                data = result.data
                response_data["emergency_numbers"] = data
        
        # If no useful content was generated, provide helpful guidance
        if not has_useful_content:
            response_parts.append("**🤖 PoisonSense AI Assistant**")
            response_parts.append("")
            response_parts.append("I'm here to help you with poison-related emergencies and information.")
            response_parts.append("")
            response_parts.append("**How can I help you?**")
            response_parts.append("• Tell me about symptoms you're observing")
            response_parts.append("• Ask about specific poisons (rat poison, paracetamol, snake bite, etc.)")
            response_parts.append("• Request first aid instructions")
            response_parts.append("• Find nearby hospitals")
            response_parts.append("")
            response_parts.append("**Example questions:**")
            response_parts.append('• "What are the symptoms of paracetamol overdose?"')
            response_parts.append('• "My child swallowed rat poison, what should I do?"')
            response_parts.append('• "Find nearest hospital"')
            response_parts.append('• "First aid for snake bite"')
            response_parts.append("")
        
        # Add emergency numbers footer (always)
        response_parts.append("---")
        response_parts.append("**🚨 Emergency Numbers (Nepal):**")
        response_parts.append("• Emergency: **102** | Poison Control: **+977-1-4412505** | Toll-Free: **1102**")
        response_parts.append("")
        response_parts.append("*⚠️ This is AI-assisted guidance. Always consult medical professionals in emergencies.*")
        
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
