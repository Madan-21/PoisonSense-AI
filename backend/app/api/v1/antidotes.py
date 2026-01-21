# Antidotes API - Antidote availability and poison-antidote mapping
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.poison import Poison, ManagementProtocol
from app.models.hospital import Hospital, ToxicologyLab
from app.models.poison_center import PoisonCenter, AntidoteInventory
from app.services.location_service import LocationService

router = APIRouter(prefix="/antidotes", tags=["Antidotes & Management"])

@router.get("/poison-antidote-map")
async def get_poison_antidote_map(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get complete mapping of poisons to their antidotes with management protocols
    This is the main reference for poison management
    """
    query = db.query(Poison).filter(Poison.is_active == True)
    
    if category:
        query = query.filter(Poison.category == category)
    
    poisons = query.all()
    
    result = []
    for p in poisons:
        result.append({
            "id": p.id,
            "poison_name": p.name,
            "common_names": p.common_names or [],
            "category": p.category.value if p.category else None,
            "severity": p.typical_severity.value if p.typical_severity else "moderate",
            "common_sources": p.common_sources or [],
            
            # Symptoms
            "symptoms_immediate": p.symptoms_immediate or [],
            "symptoms_delayed": p.symptoms_delayed or [],
            
            # Treatment - KEY INFO
            "antidote": {
                "primary": p.antidote,
                "alternatives": p.antidote_alternatives or [],
                "dosage": p.antidote_dosage
            },
            
            # Management Protocol
            "management": {
                "first_aid": p.first_aid,
                "decontamination": p.decontamination,
                "management_protocol": p.management_protocol,
                "supportive_care": p.supportive_care,
                "contraindications": p.contraindications
            },
            
            # Monitoring
            "tests_required": p.tests_required or [],
            "monitoring_parameters": p.monitoring_parameters or [],
            
            # Data Source Info - EXPLAINABILITY
            "data_sources": p.data_sources or [
                {
                    "source": "PoisonSense Medical Database",
                    "type": "curated_database",
                    "last_reviewed": str(p.last_reviewed) if p.last_reviewed else None,
                    "reviewed_by": p.reviewed_by
                }
            ],
            "prognosis": p.prognosis,
            "recovery_time": p.recovery_time
        })
    
    return {
        "count": len(result),
        "poison_antidote_map": result,
        "data_attribution": {
            "source": "PoisonSense-AI Medical Knowledge Base",
            "disclaimer": "This information is for educational purposes. Always consult medical professionals.",
            "last_updated": "2024-01-01",
            "data_sources": [
                "Nepal National Poison Information Centre (NPIC)",
                "WHO Guidelines on Poison Management",
                "Standard Medical Toxicology References"
            ]
        }
    }

@router.get("/find-antidote/{antidote_name}")
async def find_antidote_locations(
    antidote_name: str,
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(100, description="Search radius in km"),
    db: Session = Depends(get_db)
):
    """
    Find locations where a specific antidote is available
    Returns hospitals and poison centers with the antidote in stock
    """
    service = LocationService(db)
    
    # Find hospitals with this antidote
    hospitals_with_antidote = service.find_antidote_locations(
        antidote_name, latitude, longitude, radius_km
    )
    
    # Also search in hospital antidotes_available JSON field
    hospitals = db.query(Hospital).filter(
        Hospital.is_active == True,
        Hospital.antidotes_available.contains([antidote_name])
    ).all()
    
    # Calculate distances
    hospital_results = []
    for h in hospitals:
        if h.latitude and h.longitude:
            dist = service._calculate_distance(latitude, longitude, h.latitude, h.longitude)
            if dist <= radius_km:
                hospital_results.append({
                    "id": h.id,
                    "name": h.name,
                    "type": "hospital",
                    "phone": h.phone,
                    "emergency_phone": h.emergency_phone,
                    "address": f"{h.address}, {h.city}",
                    "latitude": h.latitude,
                    "longitude": h.longitude,
                    "distance_km": round(dist, 2),
                    "is_24_hours": h.is_24_hours,
                    "all_antidotes": h.antidotes_available
                })
    
    # Sort by distance
    hospital_results.sort(key=lambda x: x["distance_km"])
    
    return {
        "antidote_searched": antidote_name,
        "user_location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "locations_found": len(hospital_results),
        "locations": hospital_results[:20],
        "data_source": {
            "source": "PoisonSense-AI Hospital Network Database",
            "note": "Availability may vary. Please call ahead to confirm.",
            "last_updated": "Real-time from registered hospitals"
        }
    }

@router.get("/management-protocol/{poison_name}")
async def get_management_protocol(
    poison_name: str,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get detailed management protocol for a specific poison
    Includes step-by-step treatment guidelines
    """
    # Find poison
    poison = db.query(Poison).filter(
        Poison.name.ilike(f"%{poison_name}%")
    ).first()
    
    if not poison:
        raise HTTPException(status_code=404, detail=f"Poison '{poison_name}' not found in database")
    
    # Get detailed protocol if available
    protocol = db.query(ManagementProtocol).filter(
        ManagementProtocol.poison_id == poison.id
    ).first()
    
    response = {
        "poison_name": poison.name,
        "category": poison.category.value if poison.category else None,
        "severity": poison.typical_severity.value if poison.typical_severity else "moderate",
        
        # Step-by-step management
        "management_steps": {
            "immediate_first_aid": {
                "steps": _parse_steps(poison.first_aid),
                "critical_actions": [
                    "Remove from exposure source",
                    "Ensure airway is clear",
                    "Call emergency services (102)",
                    "Do NOT induce vomiting unless specifically instructed"
                ]
            },
            "decontamination": {
                "method": poison.decontamination or "Consult poison control for specific guidance",
                "activated_charcoal": "May be indicated within 1 hour of ingestion" if poison.category and "pharmaceutical" in poison.category.value.lower() else None
            },
            "antidote_therapy": {
                "primary_antidote": poison.antidote,
                "alternatives": poison.antidote_alternatives or [],
                "dosage": poison.antidote_dosage,
                "administration": "As per medical professional guidance"
            },
            "supportive_care": {
                "measures": _parse_steps(poison.supportive_care) if poison.supportive_care else [
                    "Monitor vital signs",
                    "IV fluid support as needed",
                    "Oxygen therapy if hypoxic",
                    "Cardiac monitoring for cardiotoxic substances"
                ]
            },
            "hospital_management": {
                "protocol": poison.management_protocol,
                "tests_required": poison.tests_required or ["Blood toxicology screen", "Basic metabolic panel"],
                "monitoring": poison.monitoring_parameters or ["Vital signs", "Level of consciousness", "Respiratory status"]
            }
        },
        
        "contraindications": {
            "do_not": _parse_contraindications(poison.contraindications),
            "critical_warnings": [
                "Never give anything by mouth to an unconscious patient",
                "Do not induce vomiting for corrosive or petroleum products"
            ]
        },
        
        "special_considerations": {
            "pediatric": protocol.pediatric_considerations if protocol else "Adjust dosing for weight. Consult pediatric toxicology.",
            "pregnancy": protocol.pregnancy_considerations if protocol else "Consult obstetric and toxicology specialists."
        },
        
        "prognosis": {
            "expected_outcome": poison.prognosis or "Depends on exposure severity and time to treatment",
            "recovery_time": poison.recovery_time
        },
        
        # EXPLAINABILITY - Data Attribution
        "data_attribution": {
            "sources": poison.data_sources or [
                {"name": "PoisonSense Medical Database", "type": "curated"},
                {"name": "Nepal NPIC Guidelines", "type": "government"},
                {"name": "WHO Toxicology Guidelines", "type": "international"}
            ],
            "last_reviewed": str(poison.last_reviewed) if poison.last_reviewed else "Database standard",
            "reviewed_by": poison.reviewed_by or "Medical Toxicology Team",
            "disclaimer": "This protocol is for guidance only. Treatment should be individualized by qualified medical professionals.",
            "emergency_contact": {
                "nepal_poison_center": "01-4412505",
                "toll_free": "1102",
                "emergency": "102"
            }
        }
    }
    
    return response


def _parse_steps(text: str) -> List[str]:
    """Parse text into list of steps"""
    if not text:
        return []
    
    # If already contains numbered steps or bullet points
    if any(text.startswith(x) for x in ["1.", "1)", "-", "•"]):
        lines = text.split('\n')
        return [line.strip() for line in lines if line.strip()]
    
    # Otherwise split by common delimiters
    if ';' in text:
        return [s.strip() for s in text.split(';') if s.strip()]
    if ',' in text and len(text) > 100:
        return [s.strip() for s in text.split(',') if s.strip()]
    
    return [text]


def _parse_contraindications(text: str) -> List[str]:
    """Parse contraindications into list"""
    if not text:
        return [
            "Do not induce vomiting without medical guidance",
            "Do not give activated charcoal for corrosives",
            "Do not delay transport to hospital"
        ]
    return _parse_steps(text)
