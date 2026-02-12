# Poison service - Main service combining ML, DB, and explainability
import time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.poison import Poison, SeverityLevel
from app.models.ai_log import AnalysisLog
from app.services.ml_service import ml_service
from app.services.explainability import ExplainabilityService
from app.services.location_service import LocationService
from app.schemas.analysis import (
    SymptomAnalysisRequest, 
    AnalysisResponse,
    PredictionResult,
    AntidoteInfo,
    NearbyResource,
    ReasoningExplanation,
    DataSourceInfo
)
from datetime import datetime

class PoisonAnalysisService:
    """
    Main service for poison analysis
    Combines ML model, medical database, and explainability
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.explainability = ExplainabilityService(db)
        self.location_service = LocationService(db)
    
    async def analyze_symptoms(
        self,
        request: SymptomAnalysisRequest,
        user_id: Optional[int] = None
    ) -> AnalysisResponse:
        """
        Main analysis function
        1. Gets ML prediction
        2. Enriches with database info
        3. Generates explanation
        4. Finds nearby help
        5. Logs for audit
        """
        start_time = time.time()
        
        # Step 1: Get ML prediction
        ml_result = ml_service.predict(request.symptoms)
        
        if ml_result.get("error"):
            # Fallback to database search if ML fails
            ml_result = await self._fallback_db_search(request.symptoms)
        
        primary_pred = ml_result.get("primary_prediction", {})
        poison_name = primary_pred.get("poison_name", "Unknown")
        confidence = primary_pred.get("confidence", 0)
        
        # Step 2: Get detailed info from database
        poison_db = self.db.query(Poison).filter(
            Poison.name.ilike(f"%{poison_name}%")
        ).first()
        
        # Build response with database enrichment
        additional_info = primary_pred.get("additional_info", {}) or {}
        
        # Determine severity
        severity = self._determine_severity(poison_db, confidence, request)
        
        # Get first aid and treatment info
        first_aid = "1. Remove person from exposure source\n2. Do not induce vomiting unless instructed\n3. Call Poison Control: 01-4412505\n4. Seek immediate medical attention"
        management = additional_info.get("management_protocol", "Seek immediate medical attention")
        antidote_name = additional_info.get("antidote")
        
        if poison_db:
            if poison_db.first_aid:
                first_aid = poison_db.first_aid
            if poison_db.management_protocol:
                management = poison_db.management_protocol
            if poison_db.antidote:
                antidote_name = poison_db.antidote
        
        # Step 3: Generate explanation
        reasoning_dict = self.explainability.generate_explanation(
            request.symptoms,
            primary_pred,
            poison_db
        )
        
        reasoning = ReasoningExplanation(
            matched_symptoms=reasoning_dict.get("matched_symptoms", []),
            symptom_match_score=reasoning_dict.get("symptom_match_score", 0),
            model_confidence=confidence,
            similar_cases_count=reasoning_dict.get("similar_cases_count", 0),
            data_sources=[
                DataSourceInfo(
                    source_name=ds.get("source_name", "Unknown"),
                    source_type=ds.get("source_type", "unknown"),
                    reliability_score=ds.get("reliability_score", 0),
                    last_updated=datetime.fromisoformat(ds["last_updated"]) if ds.get("last_updated") else None
                ) for ds in reasoning_dict.get("data_sources", [])
            ],
            reasoning_text=reasoning_dict.get("reasoning_text", "")
        )
        
        # Step 4: Find nearby help (if location provided)
        nearest_poison_center = None
        nearby_hospitals = []
        
        if request.latitude and request.longitude:
            # Find nearest poison center
            centers = self.location_service.find_nearby_poison_centers(
                request.latitude, request.longitude, radius_km=100, limit=1
            )
            if centers:
                c = centers[0]
                nearest_poison_center = NearbyResource(
                    id=c["id"],
                    name=c["name"],
                    type="poison_center",
                    distance_km=c["distance_km"],
                    phone=c["phone"],
                    address=c["address"],
                    has_antidote=bool(c.get("antidotes_available")),
                    is_24_hours=c.get("is_24_hours", True),
                    latitude=c.get("latitude"),
                    longitude=c.get("longitude")
                )
            
            # Find nearby hospitals
            hospitals = self.location_service.find_nearby_hospitals(
                request.latitude, request.longitude,
                radius_km=50, limit=5,
                antidote_name=antidote_name
            )
            nearby_hospitals = [
                NearbyResource(
                    id=h["id"],
                    name=h["name"],
                    type="hospital",
                    distance_km=h["distance_km"],
                    phone=h["phone"],
                    address=h["address"],
                    has_antidote=h.get("has_antidote", False),
                    is_24_hours=h.get("is_24_hours", False),
                    latitude=h.get("latitude"),
                    longitude=h.get("longitude")
                ) for h in hospitals
            ]
        
        # Build antidote info
        antidote_info = None
        if antidote_name:
            antidote_locations = []
            if request.latitude and request.longitude:
                antidote_locations = self.location_service.find_antidote_locations(
                    antidote_name, request.latitude, request.longitude
                )
            
            antidote_info = AntidoteInfo(
                name=antidote_name,
                generic_name=poison_db.antidote if poison_db else None,
                dosage_info=poison_db.antidote_dosage if poison_db else None,
                availability_locations=antidote_locations[:5]
            )
        
        # Step 5: Log analysis
        response_time_ms = int((time.time() - start_time) * 1000)
        
        log = self.explainability.log_analysis(
            user_id=user_id,
            input_symptoms=request.symptoms,
            prediction={
                "poison_name": poison_name,
                "confidence": confidence,
                "all_predictions": [
                    {"poison": p.get("poison_name"), "confidence": p.get("confidence")}
                    for p in ml_result.get("predictions", [])
                ]
            },
            reasoning=reasoning_dict,
            response_time_ms=response_time_ms
        )
        
        # Build response
        return AnalysisResponse(
            primary_prediction=PredictionResult(
                poison_name=poison_name,
                confidence=confidence,
                category=additional_info.get("category")
            ),
            alternative_predictions=[
                PredictionResult(
                    poison_name=p.get("poison_name", ""),
                    confidence=p.get("confidence", 0),
                    category=p.get("additional_info", {}).get("category") if p.get("additional_info") else None
                ) for p in ml_result.get("predictions", [])[1:4]  # Top 3 alternatives
            ],
            severity=severity,
            first_aid=first_aid,
            antidote=antidote_info,
            management_protocol=management,
            contraindications=poison_db.contraindications if poison_db else None,
            reasoning=reasoning,
            nearest_poison_center=nearest_poison_center,
            nearby_hospitals=nearby_hospitals,
            analysis_id=log.id,
            timestamp=datetime.utcnow()
        )
    
    def _determine_severity(
        self, 
        poison: Optional[Poison], 
        confidence: float,
        request: SymptomAnalysisRequest
    ) -> str:
        """Determine severity level based on various factors"""
        
        if poison and poison.typical_severity:
            return poison.typical_severity.value
        
        # Default logic based on keywords
        symptoms_lower = request.symptoms.lower()
        
        critical_keywords = ["unconscious", "not breathing", "seizure", "cardiac", "coma"]
        severe_keywords = ["vomiting blood", "severe pain", "difficulty breathing", "paralysis"]
        moderate_keywords = ["vomiting", "diarrhea", "confusion", "dizziness"]
        
        if any(kw in symptoms_lower for kw in critical_keywords):
            return "critical"
        elif any(kw in symptoms_lower for kw in severe_keywords):
            return "severe"
        elif any(kw in symptoms_lower for kw in moderate_keywords):
            return "moderate"
        else:
            return "mild"
    
    async def _fallback_db_search(self, symptoms: str) -> Dict:
        """Fallback search in database when ML fails"""
        symptoms_list = [s.strip().lower() for s in symptoms.split(',')]
        
        # Search poisons by symptoms
        poisons = self.db.query(Poison).all()
        
        matches = []
        for poison in poisons:
            score = 0
            all_symptoms = []
            
            if poison.symptoms_immediate:
                all_symptoms.extend(poison.symptoms_immediate if isinstance(poison.symptoms_immediate, list) else [])
            if poison.symptoms_delayed:
                all_symptoms.extend(poison.symptoms_delayed if isinstance(poison.symptoms_delayed, list) else [])
            
            for s in symptoms_list:
                if any(s in str(ps).lower() for ps in all_symptoms):
                    score += 1
            
            if score > 0:
                matches.append({
                    "poison_name": poison.name,
                    "confidence": min(score / len(symptoms_list), 0.9),
                    "additional_info": {
                        "category": poison.category.value if poison.category else None,
                        "antidote": poison.antidote,
                        "management_protocol": poison.management_protocol
                    }
                })
        
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "success": True,
            "predictions": matches[:5],
            "primary_prediction": matches[0] if matches else {"poison_name": "Unknown", "confidence": 0}
        }
    
    def get_user_history(self, user_id: int, limit: int = 20) -> List[AnalysisLog]:
        """Get user's analysis history"""
        return self.db.query(AnalysisLog).filter(
            AnalysisLog.user_id == user_id
        ).order_by(AnalysisLog.created_at.desc()).limit(limit).all()
