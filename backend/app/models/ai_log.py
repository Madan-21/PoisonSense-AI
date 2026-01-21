# AI log model - For explainability and audit trail
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class AnalysisLog(Base):
    """Log of all AI analyses - for explainability and audit"""
    __tablename__ = "analysis_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Input
    input_symptoms = Column(Text, nullable=False)  # Original symptom text
    input_additional_info = Column(JSON)  # Age, weight, time since exposure, etc.
    
    # ML Prediction
    predicted_poison = Column(String(255))
    confidence_score = Column(Float)
    
    # Top predictions with confidence
    all_predictions = Column(JSON)  # [{"poison": "Arsenic", "confidence": 0.85}, ...]
    
    # Matched from database
    matched_poison_id = Column(Integer, ForeignKey("poisons.id"))
    
    # Response given
    antidote_suggested = Column(String(255))
    management_protocol = Column(Text)
    severity_assessment = Column(String(50))
    
    # EXPLAINABILITY - Why this prediction
    reasoning = Column(JSON)  # {
        # "matched_symptoms": ["nausea", "abdominal pain"],
        # "symptom_match_score": 0.78,
        # "data_source": "WHO Poison Database",
        # "similar_cases": 15,
        # "model_version": "v1.0"
    # }
    
    # Data sources used
    data_sources_used = Column(JSON)  # ["Medical Knowledge DB", "Poison Database"]
    
    # Actions taken
    emergency_contacted = Column(Boolean, default=False)
    doctor_consulted = Column(Boolean, default=False)
    hospital_referred = Column(Boolean, default=False)
    
    # User feedback (optional)
    user_feedback = Column(String(50))  # "helpful", "not_helpful", "incorrect"
    feedback_notes = Column(Text)
    
    # Location (if provided)
    user_latitude = Column(Float)
    user_longitude = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer)  # How long the analysis took
    
    # Relationships
    user = relationship("User", back_populates="analysis_history")


class AIModelVersion(Base):
    """Track AI model versions for accountability"""
    __tablename__ = "ai_model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    version = Column(String(50), nullable=False, unique=True)
    model_type = Column(String(100))  # "DistilBERT", "Custom"
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Training info
    training_data_size = Column(Integer)
    training_date = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
