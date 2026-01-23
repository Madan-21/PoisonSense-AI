# Core AI endpoint - Poison Analysis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.models.poison import Poison
from app.schemas.analysis import (
    SymptomAnalysisRequest,
    AnalysisResponse,
    AnalysisHistoryItem
)
from app.services.poison_service import PoisonAnalysisService
from app.services.ml_service import ml_service
from app.core.security import get_current_active_user, get_current_user

router = APIRouter(prefix="/analysis", tags=["Poison Analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Analyze symptoms and predict possible poisoning
    
    This is the main AI endpoint that:
    1. Uses ML model to predict poison type
    2. Enriches with medical database info
    3. Provides explainable reasoning
    4. Finds nearby help resources
    
    Can be used with or without authentication.
    Authenticated users get their analysis logged for history.
    """
    service = PoisonAnalysisService(db)
    
    user_id = current_user.id if current_user else None
    
    try:
        result = await service.analyze_symptoms(request, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/history", response_model=List[AnalysisHistoryItem])
async def get_analysis_history(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's analysis history"""
    service = PoisonAnalysisService(db)
    history = service.get_user_history(current_user.id, limit)
    return [AnalysisHistoryItem.model_validate(h) for h in history]

@router.get("/model-info")
async def get_model_info():
    """Get information about the ML model"""
    return ml_service.get_model_info()

# ============ Poison Database Lookup ============

@router.get("/poisons", response_model=List[dict])
async def list_poisons(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List poisons from the database"""
    query = db.query(Poison).filter(Poison.is_active == True)
    
    if category:
        query = query.filter(Poison.category == category)
    
    if search:
        query = query.filter(
            Poison.name.ilike(f"%{search}%") |
            Poison.common_names.contains([search])
        )
    
    poisons = query.limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category.value if p.category else None,
            "common_names": p.common_names,
            "antidote": p.antidote,
            "typical_severity": p.typical_severity.value if p.typical_severity else None
        }
        for p in poisons
    ]

@router.get("/poisons/{poison_id}")
async def get_poison_details(
    poison_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific poison"""
    poison = db.query(Poison).filter(Poison.id == poison_id).first()
    
    if not poison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poison not found"
        )
    
    return {
        "id": poison.id,
        "name": poison.name,
        "category": poison.category.value if poison.category else None,
        "common_names": poison.common_names,
        "common_sources": poison.common_sources,
        "symptoms_immediate": poison.symptoms_immediate,
        "symptoms_delayed": poison.symptoms_delayed,
        "typical_severity": poison.typical_severity.value if poison.typical_severity else None,
        "first_aid": poison.first_aid,
        "antidote": poison.antidote,
        "antidote_dosage": poison.antidote_dosage,
        "management_protocol": poison.management_protocol,
        "contraindications": poison.contraindications,
        "tests_required": poison.tests_required,
        "data_sources": poison.data_sources,
        "last_reviewed": poison.last_reviewed,
        "reviewed_by": poison.reviewed_by
    }
