# Agentic AI API Endpoint
# Main endpoint for the conversational AI agent

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.agentic_ai_service import create_agent, PoisonSenseAgent

router = APIRouter(prefix="/agent", tags=["Agentic AI"])


# =============================================================================
# Request/Response Models
# =============================================================================

class AgentMessageRequest(BaseModel):
    """Request for agent conversation"""
    message: str = Field(..., description="User message to the agent", min_length=1, max_length=2000)
    latitude: Optional[float] = Field(None, description="User's latitude for location-based services")
    longitude: Optional[float] = Field(None, description="User's longitude for location-based services")
    session_id: Optional[str] = Field(None, description="Session ID to continue previous conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "My child accidentally swallowed some rat poison about 30 minutes ago. What should I do?",
                "latitude": 27.7172,
                "longitude": 85.3240
            }
        }


class EmergencyInfo(BaseModel):
    """Emergency information"""
    emergency: str
    poison_control: str
    toll_free: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from agent"""
    message: str = Field(..., description="Agent's response message")
    is_emergency: bool = Field(False, description="Whether this is an emergency situation")
    severity: Optional[str] = Field(None, description="Assessed severity level")
    identified_poison: Optional[str] = Field(None, description="Identified or suspected poison")
    confidence: Optional[float] = Field(None, description="Confidence in identification")
    first_aid: Optional[List[str]] = Field(None, description="First aid steps if applicable")
    antidote: Optional[Any] = Field(None, description="Antidote information (can be dict or string)")
    nearby_hospitals: Optional[List[Dict]] = Field(None, description="Nearby hospitals")
    emergency_numbers: Optional[Dict] = Field(None, description="Emergency contact numbers")
    tools_used: Optional[List[str]] = Field(None, description="Tools used to generate response")
    session_id: Optional[str] = Field(None, description="Session ID for continuation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "🚨 **EMERGENCY DETECTED**...",
                "is_emergency": True,
                "severity": "CRITICAL",
                "identified_poison": "Rat Poison (Anticoagulant)",
                "confidence": 0.85,
                "tools_used": ["analyze_symptoms", "get_first_aid", "find_nearby_hospitals"]
            }
        }


class PoisonSearchRequest(BaseModel):
    """Request to search poison database"""
    query: str = Field(..., description="Search query", min_length=1, max_length=200)


class PoisonInfoRequest(BaseModel):
    """Request for poison information"""
    poison_name: str = Field(..., description="Name of poison to look up")


class SeverityAssessmentRequest(BaseModel):
    """Request for severity assessment"""
    symptoms: str = Field(..., description="Symptoms to assess")
    poison_name: Optional[str] = Field(None, description="Known or suspected poison")


class SymptomAnalysisRequest(BaseModel):
    """Request for symptom analysis"""
    symptoms: str = Field(..., description="Symptoms to analyze")


# =============================================================================
# Session Management
# =============================================================================

# In-memory session storage (in production, use Redis or database)
_agent_sessions: Dict[str, PoisonSenseAgent] = {}


def get_or_create_agent(session_id: Optional[str], db: Session) -> tuple[PoisonSenseAgent, str]:
    """Get existing agent session or create new one"""
    import uuid
    
    if session_id and session_id in _agent_sessions:
        agent = _agent_sessions[session_id]
        agent.db = db  # Update DB session
        return agent, session_id
    
    # Create new session
    new_session_id = str(uuid.uuid4())
    agent = create_agent(db)
    _agent_sessions[new_session_id] = agent
    
    # Cleanup old sessions (keep max 1000)
    if len(_agent_sessions) > 1000:
        oldest_keys = list(_agent_sessions.keys())[:100]
        for key in oldest_keys:
            del _agent_sessions[key]
    
    return agent, new_session_id


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentMessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Main conversational endpoint for the Agentic AI
    
    This endpoint:
    1. Accepts natural language messages about poisoning situations
    2. Uses tools to analyze symptoms, find resources, and provide guidance
    3. Maintains conversation context within a session
    4. Prioritizes emergency situations
    
    The agent can:
    - Analyze symptoms and identify possible poisons
    - Provide first aid instructions
    - Look up antidotes and treatment protocols
    - Find nearby hospitals and poison centers
    - Assess severity and triage cases
    """
    agent, session_id = get_or_create_agent(request.session_id, db)
    
    try:
        response = await agent.process_message(
            user_message=request.message,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        return AgentResponse(
            message=response.get("message", "I apologize, but I couldn't process your request."),
            is_emergency=response.get("is_emergency", False),
            severity=response.get("severity"),
            identified_poison=response.get("identified_poison"),
            confidence=response.get("confidence"),
            first_aid=response.get("first_aid"),
            antidote=response.get("antidote"),
            nearby_hospitals=response.get("nearby_hospitals"),
            emergency_numbers=response.get("emergency_numbers"),
            tools_used=response.get("tools_used"),
            session_id=session_id
        )
        
    except Exception as e:
        # Even on error, provide emergency info
        return AgentResponse(
            message=f"""I encountered an error processing your request, but here's critical information:

**🚨 Emergency Numbers (Nepal):**
• Emergency: **102**
• Poison Control (NPIC-TUTH): **+977-1-4412505**
• Toll-Free: **1102**

If this is an emergency, please call immediately.

Error details: {str(e)}""",
            is_emergency=False,
            session_id=session_id,
            emergency_numbers={
                "emergency": "102",
                "poison_control": "+977-1-4412505",
                "toll_free": "1102"
            }
        )


@router.post("/analyze-symptoms")
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze symptoms to identify possible poisoning
    
    Uses ML model and comprehensive toxicology database to identify
    the most likely poison based on reported symptoms.
    """
    agent = create_agent(db)
    
    result = agent._tool_analyze_symptoms(request.symptoms)
    
    return {
        "analysis": result,
        "emergency_numbers": {
            "emergency": "102",
            "poison_control": "+977-1-4412505",
            "toll_free": "1102"
        },
        "disclaimer": "This is AI-assisted analysis. Always consult medical professionals."
    }


@router.post("/assess-severity")
async def assess_severity(
    request: SeverityAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Assess the severity of a poisoning case
    
    Returns severity level (CRITICAL, SEVERE, MODERATE, MILD)
    and recommended actions.
    """
    agent = create_agent(db)
    
    result = agent._tool_assess_severity(
        symptoms=request.symptoms,
        poison_name=request.poison_name
    )
    
    return result


@router.post("/search-poisons")
async def search_poison_database(
    request: PoisonSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search the comprehensive poison database
    
    Search by poison name, common names, category, or source.
    """
    agent = create_agent(db)
    
    results = agent._tool_search_poison_database(request.query)
    
    return {
        "query": request.query,
        "results": results,
        "total_found": len(results)
    }


@router.get("/poison/{poison_name}")
async def get_poison_info(
    poison_name: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive information about a specific poison
    
    Returns detailed information including:
    - Symptoms (immediate and delayed)
    - Antidotes and dosing
    - First aid instructions
    - Management protocol
    - Tests required
    - Contraindications
    """
    agent = create_agent(db)
    
    poison_info = agent._tool_get_poison_info(poison_name)
    
    if poison_info.get("error"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=poison_info["error"]
        )
    
    return poison_info


@router.get("/poison/{poison_name}/first-aid")
async def get_first_aid(
    poison_name: str,
    db: Session = Depends(get_db)
):
    """
    Get first aid instructions for a specific poison
    """
    agent = create_agent(db)
    
    return agent._tool_get_first_aid(poison_name)


@router.get("/poison/{poison_name}/antidote")
async def get_antidote_info(
    poison_name: str,
    db: Session = Depends(get_db)
):
    """
    Get antidote information for a specific poison
    
    Includes dosing information and administration guidelines.
    """
    agent = create_agent(db)
    
    return agent._tool_get_antidote(poison_name)


@router.get("/poison/{poison_name}/protocol")
async def get_management_protocol(
    poison_name: str,
    db: Session = Depends(get_db)
):
    """
    Get hospital management protocol for a specific poison
    
    Includes:
    - Step-by-step management
    - Required tests
    - Monitoring parameters
    - Contraindications
    """
    agent = create_agent(db)
    
    return agent._tool_get_management_protocol(poison_name)


@router.get("/hospitals/nearby")
async def find_nearby_hospitals(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    antidote: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Find nearby hospitals with toxicology capabilities
    
    Optionally filter by antidote availability.
    """
    agent = create_agent(db)
    
    return agent._tool_find_nearby_hospitals(
        latitude=latitude,
        longitude=longitude,
        antidote=antidote
    )


@router.get("/poison-centers/nearby")
async def find_nearby_poison_centers(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Find nearby poison control centers
    """
    agent = create_agent(db)
    
    return agent._tool_find_poison_centers(
        latitude=latitude,
        longitude=longitude
    )


@router.get("/emergency-numbers")
async def get_emergency_numbers(
    country: str = "nepal"
):
    """
    Get emergency contact numbers by country
    """
    from app.ml.data.comprehensive_toxicology_data import EMERGENCY_NUMBERS
    
    numbers = EMERGENCY_NUMBERS.get(country.lower())
    
    if not numbers:
        numbers = EMERGENCY_NUMBERS.get("nepal")
    
    return numbers


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    End a conversation session
    
    Clears the conversation context and frees resources.
    """
    if session_id in _agent_sessions:
        del _agent_sessions[session_id]
        return {"message": "Session ended successfully"}
    
    return {"message": "Session not found or already ended"}


@router.get("/session/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get summary of a conversation session
    """
    if session_id not in _agent_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    agent = _agent_sessions[session_id]
    return agent.get_conversation_summary()


# =============================================================================
# Comprehensive Poison List Endpoint
# =============================================================================

@router.get("/poisons/list")
async def list_all_poisons():
    """
    List all poisons in the comprehensive database
    
    Returns summary information for all available poisons.
    """
    from app.ml.data.comprehensive_toxicology_data import COMPREHENSIVE_POISONS
    
    poisons = []
    for poison_id, data in COMPREHENSIVE_POISONS.items():
        antidote = data.get("antidote", {})
        if isinstance(antidote, dict):
            antidote_name = antidote.get("primary", "Supportive care")
        else:
            antidote_name = antidote or "Supportive care"
        
        poisons.append({
            "id": poison_id,
            "name": data.get("name"),
            "category": data.get("category"),
            "common_names": data.get("common_names", [])[:5],
            "antidote": antidote_name,
            "typical_severity": data.get("typical_severity") if isinstance(data.get("typical_severity"), str) else "varies"
        })
    
    return {
        "total": len(poisons),
        "poisons": poisons
    }


@router.get("/categories")
async def get_poison_categories():
    """
    Get list of poison categories
    """
    from app.ml.data.comprehensive_toxicology_data import COMPREHENSIVE_POISONS
    
    categories = set()
    for data in COMPREHENSIVE_POISONS.values():
        cat = data.get("category")
        if cat:
            categories.add(cat)
    
    return {
        "categories": sorted(list(categories))
    }
