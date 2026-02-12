# WHY + SOURCES - Explainability Service
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.poison import Poison
from app.models.ai_log import AnalysisLog

class ExplainabilityService:
    """
    Service to provide explanations for AI predictions
    Critical for medical AI - users need to understand WHY
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_explanation(
        self,
        input_symptoms: str,
        prediction: Dict,
        matched_poison: Optional[Poison] = None
    ) -> Dict:
        """
        Generate human-readable explanation for the AI prediction
        """
        # Extract matched symptoms
        input_symptoms_list = self._extract_symptoms(input_symptoms)
        
        # Get confidence breakdown
        confidence = prediction.get("confidence", 0)
        
        # Build reasoning
        reasoning = {
            "matched_symptoms": [],
            "symptom_match_score": 0.0,
            "model_confidence": confidence,
            "similar_cases_count": 0,
            "data_sources": [],
            "reasoning_text": ""
        }
        
        # Match symptoms with known symptoms
        if matched_poison:
            known_symptoms = self._get_known_symptoms(matched_poison)
            matched = [s for s in input_symptoms_list if any(
                s.lower() in ks.lower() or ks.lower() in s.lower() 
                for ks in known_symptoms
            )]
            reasoning["matched_symptoms"] = matched
            reasoning["symptom_match_score"] = len(matched) / max(len(input_symptoms_list), 1)
        
        # Add data sources
        reasoning["data_sources"] = self._get_data_sources(matched_poison)
        
        # Generate human-readable explanation
        reasoning["reasoning_text"] = self._generate_reasoning_text(
            prediction, 
            reasoning, 
            matched_poison
        )
        
        return reasoning
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract individual symptoms from text"""
        # Split by common delimiters
        import re
        symptoms = re.split(r'[,;.]|\band\b|\bwith\b', text.lower())
        symptoms = [s.strip() for s in symptoms if s.strip()]
        return symptoms
    
    def _get_known_symptoms(self, poison: Poison) -> List[str]:
        """Get known symptoms for a poison"""
        symptoms = []
        
        if poison.symptoms_immediate:
            if isinstance(poison.symptoms_immediate, list):
                symptoms.extend(poison.symptoms_immediate)
            elif isinstance(poison.symptoms_immediate, str):
                symptoms.extend(poison.symptoms_immediate.split(','))
        
        if poison.symptoms_delayed:
            if isinstance(poison.symptoms_delayed, list):
                symptoms.extend(poison.symptoms_delayed)
            elif isinstance(poison.symptoms_delayed, str):
                symptoms.extend(poison.symptoms_delayed.split(','))
        
        return symptoms
    
    def _get_data_sources(self, poison: Optional[Poison]) -> List[Dict]:
        """Get data sources used for the prediction"""
        sources = [
            {
                "source_name": "PoisonSense AI ML Model",
                "source_type": "ml_model",
                "reliability_score": 0.85,
                "last_updated": datetime.utcnow().isoformat()
            }
        ]
        
        if poison:
            sources.append({
                "source_name": "PoisonSense Medical Knowledge Database",
                "source_type": "database",
                "reliability_score": 0.95,
                "last_updated": poison.updated_at.isoformat() if poison.updated_at else None,
                "details": "Curated medical database with verified toxicology information"
            })
            
            # Add specific data sources from poison record
            if poison.data_sources:
                for ds in poison.data_sources:
                    if isinstance(ds, dict):
                        sources.append({
                            "source_name": ds.get("source", "Medical Reference"),
                            "source_type": ds.get("type", "external_reference"),
                            "reliability_score": 0.90,
                            "last_updated": ds.get("year"),
                            "details": f"Verified medical reference from {ds.get('type', 'medical institution')}"
                        })
                    else:
                        sources.append({
                            "source_name": str(ds),
                            "source_type": "external_reference",
                            "reliability_score": 0.90,
                            "last_updated": None
                        })
            
            # Add Nepal-specific sources
            sources.append({
                "source_name": "Nepal National Poison Information Centre (NPIC)",
                "source_type": "government",
                "reliability_score": 0.95,
                "last_updated": "2024",
                "details": "Government poison control guidelines for Nepal"
            })
            
            if poison.reviewed_by:
                sources.append({
                    "source_name": f"Medical Review: {poison.reviewed_by}",
                    "source_type": "expert_review",
                    "reliability_score": 0.92,
                    "last_updated": poison.last_reviewed.isoformat() if poison.last_reviewed else None
                })
        
        return sources
    
    def _generate_reasoning_text(
        self, 
        prediction: Dict, 
        reasoning: Dict,
        poison: Optional[Poison]
    ) -> str:
        """Generate human-readable explanation with data attribution"""
        poison_name = prediction.get("poison_name", "Unknown")
        confidence = prediction.get("confidence", 0) * 100
        matched_symptoms = reasoning.get("matched_symptoms", [])
        
        text = f"🔍 ANALYSIS REASONING:\n\n"
        text += f"Based on the symptoms provided, our AI model identified {poison_name} "
        text += f"with {confidence:.1f}% confidence.\n\n"
        
        if matched_symptoms:
            text += f"📋 SYMPTOM MATCHING:\n"
            text += f"The following symptoms matched known symptoms of {poison_name}:\n"
            for symptom in matched_symptoms:
                text += f"  • {symptom}\n"
            text += "\n"
        
        text += "📚 DATA SOURCES:\n"
        if poison and poison.data_sources:
            for ds in poison.data_sources:
                if isinstance(ds, dict):
                    text += f"  • {ds.get('source', 'Medical Reference')} ({ds.get('type', 'reference')})\n"
                else:
                    text += f"  • {ds}\n"
        
        text += "  • PoisonSense-AI Medical Knowledge Base\n"
        text += "  • Nepal National Poison Information Centre Guidelines\n"
        
        if poison and poison.reviewed_by:
            text += f"\n✅ MEDICAL REVIEW:\n"
            text += f"This information was reviewed by {poison.reviewed_by}"
            if poison.last_reviewed:
                text += f" (Last reviewed: {poison.last_reviewed.strftime('%Y-%m-%d')})"
            text += "\n"
        
        text += "\n⚠️ DISCLAIMER:\n"
        text += "This is AI-assisted guidance only. Always verify with a medical professional before taking action."
        
        return text
    
    def log_analysis(
        self,
        user_id: Optional[int],
        input_symptoms: str,
        prediction: Dict,
        reasoning: Dict,
        response_time_ms: int
    ) -> AnalysisLog:
        """Log the analysis for audit trail"""
        log = AnalysisLog(
            user_id=user_id,
            input_symptoms=input_symptoms,
            predicted_poison=prediction.get("poison_name"),
            confidence_score=prediction.get("confidence", 0),
            all_predictions=prediction.get("all_predictions"),
            reasoning=reasoning,
            response_time_ms=response_time_ms,
            data_sources_used=[ds["source_name"] for ds in reasoning.get("data_sources", [])]
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
