# Analysis schemas - For AI poison analysis
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SymptomAnalysisRequest(BaseModel):
    """Request for AI poison analysis"""
    symptoms: str = Field(..., min_length=3, description="Symptoms description")
    
    # Optional additional info for better analysis
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    time_since_exposure: Optional[str] = None  # e.g., "30 minutes", "2 hours"
    suspected_substance: Optional[str] = None
    exposure_route: Optional[str] = None  # "ingestion", "inhalation", "skin contact"
    quantity_exposed: Optional[str] = None
    
    # Location for nearby help
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PredictionResult(BaseModel):
    """Single prediction result"""
    poison_name: str
    confidence: float
    category: Optional[str] = None

class DataSourceInfo(BaseModel):
    """Information about where data came from - for explainability"""
    source_name: str
    source_type: str  # "database", "ml_model", "external_api"
    reliability_score: float  # 0-1
    last_updated: Optional[datetime] = None

class ReasoningExplanation(BaseModel):
    """Explanation of AI reasoning - EXPLAINABILITY"""
    matched_symptoms: List[str]
    symptom_match_score: float
    model_confidence: float
    similar_cases_count: int
    data_sources: List[DataSourceInfo]
    reasoning_text: str  # Human-readable explanation

class AntidoteInfo(BaseModel):
    """Antidote information"""
    name: str
    generic_name: Optional[str] = None
    dosage_info: Optional[str] = None
    availability_locations: List[Dict[str, Any]] = []  # Nearby places with this antidote

class NearbyResource(BaseModel):
    """Nearby hospital/poison center"""
    id: int
    name: str
    type: str  # "hospital", "poison_center"
    distance_km: Optional[float] = None
    phone: str
    address: str
    has_antidote: bool = False
    is_24_hours: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AnalysisResponse(BaseModel):
    """Complete response from AI analysis"""
    # Prediction results
    primary_prediction: PredictionResult
    alternative_predictions: List[PredictionResult] = []
    
    # Medical info
    severity: str  # "mild", "moderate", "severe", "critical"
    
    # Treatment info
    first_aid: str
    antidote: Optional[AntidoteInfo] = None
    management_protocol: str
    contraindications: Optional[str] = None
    
    # EXPLAINABILITY - Critical for trust
    reasoning: ReasoningExplanation
    
    # Nearby help
    nearest_poison_center: Optional[NearbyResource] = None
    nearby_hospitals: List[NearbyResource] = []
    
    # Emergency info
    emergency_numbers: Dict[str, str] = {
        "emergency_services": "102",
        "poison_control": "01-512345",
        "crisis_hotline": "100"
    }
    
    # Metadata
    analysis_id: int
    timestamp: datetime
    disclaimer: str = "This is AI-assisted guidance only. Always consult medical professionals in emergencies."

class AnalysisHistoryItem(BaseModel):
    """Item in user's analysis history"""
    id: int
    input_symptoms: str
    predicted_poison: str
    confidence_score: float
    severity_assessment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
