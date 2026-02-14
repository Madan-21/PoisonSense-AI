# Poison Syndromes API - Toxidrome patterns for AI use
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.models.poison_syndrome import PoisonSyndrome

router = APIRouter(prefix="/poison-syndromes", tags=["Poison Syndromes"])

@router.get("/")
async def list_poison_syndromes(
    db: Session = Depends(get_db),
    is_active: Optional[bool] = True
):
    """
    List all poison syndromes/toxidromes
    
    This endpoint provides clinical presentation patterns for poison identification.
    The AI uses this data to match symptoms to potential syndromes.
    """
    query = db.query(PoisonSyndrome)
    
    if is_active is not None:
        query = query.filter(PoisonSyndrome.is_active == is_active)
    
    syndromes = query.all()
    
    return {
        "syndromes": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "common_agents": s.common_agents,
                "mental_status": s.mental_status,
                "vital_signs": s.vital_signs,
                "pupils": s.pupils,
                "skin": s.skin,
                "other_features": s.other_features,
                "treatment_priorities": s.treatment_priorities,
                "specific_antidotes": s.specific_antidotes,
                "supportive_care": s.supportive_care
            }
            for s in syndromes
        ]
    }

@router.get("/{syndrome_id}")
async def get_syndrome_details(
    syndrome_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific poison syndrome"""
    syndrome = db.query(PoisonSyndrome).filter(PoisonSyndrome.id == syndrome_id).first()
    
    if not syndrome:
        return {"error": "Syndrome not found"}, 404
    
    return {
        "id": syndrome.id,
        "name": syndrome.name,
        "description": syndrome.description,
        "common_agents": syndrome.common_agents,
        "mental_status": syndrome.mental_status,
        "vital_signs": syndrome.vital_signs,
        "pupils": syndrome.pupils,
        "skin": syndrome.skin,
        "other_features": syndrome.other_features,
        "treatment_priorities": syndrome.treatment_priorities,
        "specific_antidotes": syndrome.specific_antidotes,
        "supportive_care": syndrome.supportive_care
    }

@router.get("/search/by-symptoms")
async def search_syndromes_by_symptoms(
    symptoms: str = Query(..., description="Comma-separated symptoms"),
    db: Session = Depends(get_db)
):
    """
    Search for matching poison syndromes based on symptoms
    
    This helps the AI narrow down potential syndromes based on observed symptoms.
    """
    symptom_list = [s.strip().lower() for s in symptoms.split(",")]
    
    syndromes = db.query(PoisonSyndrome).filter(PoisonSyndrome.is_active == True).all()
    
    matches = []
    for syndrome in syndromes:
        match_score = 0
        matched_features = []
        
        # Check mental status
        if syndrome.mental_status:
            for symptom in symptom_list:
                for mental in syndrome.mental_status:
                    if symptom in mental.lower():
                        match_score += 1
                        matched_features.append(f"Mental: {mental}")
        
        # Check other features
        if syndrome.other_features:
            for symptom in symptom_list:
                for feature in syndrome.other_features:
                    if symptom in feature.lower():
                        match_score += 1
                        matched_features.append(f"Feature: {feature}")
        
        if match_score > 0:
            matches.append({
                "syndrome": syndrome.name,
                "match_score": match_score,
                "matched_features": matched_features,
                "common_agents": syndrome.common_agents,
                "treatment_priorities": syndrome.treatment_priorities,
                "specific_antidotes": syndrome.specific_antidotes
            })
    
    # Sort by match score
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "query_symptoms": symptom_list,
        "matches": matches[:5]  # Return top 5 matches
    }
