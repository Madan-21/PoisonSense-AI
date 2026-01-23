# Toxicology Labs API - Lab locations and available tests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.hospital import Hospital, ToxicologyLab
from app.services.location_service import LocationService

router = APIRouter(prefix="/labs", tags=["Toxicology Labs"])

@router.get("/")
async def list_toxicology_labs(
    city: Optional[str] = None,
    test_type: Optional[str] = None,
    is_24_hours: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all toxicology labs with their available tests
    """
    # Get labs from ToxicologyLab table
    query = db.query(ToxicologyLab).filter(ToxicologyLab.is_active == True)
    
    if is_24_hours is not None:
        query = query.filter(ToxicologyLab.is_24_hours == is_24_hours)
    
    labs = query.all()
    
    # Also get hospitals with toxicology facilities
    hospital_query = db.query(Hospital).filter(
        Hospital.is_active == True,
        Hospital.facilities.contains(["Toxicology"])
    )
    
    if city:
        hospital_query = hospital_query.filter(Hospital.city.ilike(f"%{city}%"))
    
    hospitals_with_labs = hospital_query.all()
    
    result = []
    
    # Format dedicated labs
    for lab in labs:
        hospital = db.query(Hospital).filter(Hospital.id == lab.hospital_id).first()
        result.append({
            "id": lab.id,
            "name": lab.name,
            "type": "dedicated_lab",
            "hospital_name": hospital.name if hospital else None,
            "phone": lab.phone or (hospital.phone if hospital else None),
            "address": hospital.address if hospital else None,
            "city": hospital.city if hospital else None,
            "latitude": hospital.latitude if hospital else None,
            "longitude": hospital.longitude if hospital else None,
            "tests_available": lab.tests_available or [],
            "operating_hours": lab.operating_hours,
            "is_24_hours": lab.is_24_hours
        })
    
    # Format hospitals with toxicology
    for h in hospitals_with_labs:
        # Check if not already added as dedicated lab
        already_added = any(r.get("hospital_name") == h.name for r in result)
        if not already_added:
            result.append({
                "id": h.id,
                "name": f"{h.name} - Toxicology Unit",
                "type": "hospital_unit",
                "hospital_name": h.name,
                "phone": h.phone,
                "emergency_phone": h.emergency_phone,
                "address": h.address,
                "city": h.city,
                "latitude": h.latitude,
                "longitude": h.longitude,
                "tests_available": h.toxicology_tests or _get_standard_tests(),
                "is_24_hours": h.is_24_hours,
                "facilities": h.facilities
            })
    
    return {
        "count": len(result),
        "labs": result,
        "data_attribution": {
            "source": "PoisonSense-AI Healthcare Network",
            "note": "Test availability and pricing may vary. Please contact the lab directly."
        }
    }

@router.get("/nearby")
async def find_nearby_labs(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(50, description="Search radius in km"),
    test_type: Optional[str] = Query(None, description="Filter by specific test"),
    db: Session = Depends(get_db)
):
    """
    Find toxicology labs near user location
    """
    service = LocationService(db)
    
    # Get all hospitals with toxicology facilities
    hospitals = db.query(Hospital).filter(
        Hospital.is_active == True,
        Hospital.latitude.isnot(None),
        Hospital.longitude.isnot(None)
    ).all()
    
    results = []
    
    for h in hospitals:
        # Check if has toxicology
        has_tox = False
        if h.facilities:
            has_tox = any("toxicology" in f.lower() or "tox" in f.lower() for f in h.facilities)
        
        if not has_tox and not h.toxicology_tests:
            continue
        
        # Calculate distance
        dist = service._calculate_distance(latitude, longitude, h.latitude, h.longitude)
        
        if dist <= radius_km:
            tests = h.toxicology_tests or _get_standard_tests()
            
            # Filter by test type if specified
            if test_type:
                tests = [t for t in tests if test_type.lower() in str(t).lower()]
                if not tests:
                    continue
            
            results.append({
                "id": h.id,
                "name": h.name,
                "type": h.hospital_type.value if h.hospital_type else "hospital",
                "phone": h.phone,
                "emergency_phone": h.emergency_phone,
                "address": f"{h.address}, {h.city}",
                "latitude": h.latitude,
                "longitude": h.longitude,
                "distance_km": round(dist, 2),
                "tests_available": tests,
                "is_24_hours": h.is_24_hours,
                "is_verified": h.is_verified
            })
    
    # Sort by distance
    results.sort(key=lambda x: x["distance_km"])
    
    return {
        "user_location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "labs_found": len(results),
        "labs": results[:20],
        "data_attribution": {
            "source": "PoisonSense-AI Hospital Network",
            "disclaimer": "Test availability may vary. Please call ahead."
        }
    }

@router.get("/tests-catalog")
async def get_tests_catalog(db: Session = Depends(get_db)):
    """
    Get catalog of all toxicology tests with descriptions
    """
    tests = [
        {
            "name": "Blood Toxicology Screen",
            "description": "Comprehensive blood test for common toxins and drugs",
            "sample_type": "Blood",
            "turnaround_time": "2-4 hours (stat), 24 hours (routine)",
            "detects": ["Drugs of abuse", "Alcohol", "Common poisons", "Heavy metals"],
            "price_range": "NPR 1,500 - 5,000"
        },
        {
            "name": "Urine Drug Screen",
            "description": "Detection of drugs and metabolites in urine",
            "sample_type": "Urine",
            "turnaround_time": "1-2 hours",
            "detects": ["Opioids", "Benzodiazepines", "Amphetamines", "Cannabis", "Cocaine"],
            "price_range": "NPR 800 - 2,000"
        },
        {
            "name": "Acetaminophen Level",
            "description": "Quantitative measurement of paracetamol/acetaminophen",
            "sample_type": "Blood",
            "turnaround_time": "1 hour",
            "detects": ["Acetaminophen (Paracetamol)"],
            "clinical_use": "Assessment of paracetamol overdose using Rumack-Matthew nomogram",
            "price_range": "NPR 500 - 1,000"
        },
        {
            "name": "Cholinesterase Level",
            "description": "Measures cholinesterase enzyme activity",
            "sample_type": "Blood",
            "turnaround_time": "2-4 hours",
            "detects": ["Organophosphate poisoning", "Carbamate poisoning"],
            "clinical_use": "Diagnosis and monitoring of organophosphate/carbamate poisoning",
            "price_range": "NPR 600 - 1,200"
        },
        {
            "name": "Heavy Metal Panel",
            "description": "Detection of toxic heavy metals",
            "sample_type": "Blood/Urine",
            "turnaround_time": "24-48 hours",
            "detects": ["Lead", "Mercury", "Arsenic", "Cadmium", "Chromium"],
            "price_range": "NPR 2,000 - 5,000"
        },
        {
            "name": "Carbon Monoxide Level",
            "description": "Carboxyhemoglobin measurement",
            "sample_type": "Blood (arterial)",
            "turnaround_time": "30 minutes",
            "detects": ["Carbon monoxide poisoning"],
            "price_range": "NPR 400 - 800"
        },
        {
            "name": "Salicylate Level",
            "description": "Aspirin/salicylate quantification",
            "sample_type": "Blood",
            "turnaround_time": "1-2 hours",
            "detects": ["Aspirin overdose"],
            "price_range": "NPR 500 - 1,000"
        },
        {
            "name": "Ethanol Level",
            "description": "Blood alcohol concentration",
            "sample_type": "Blood",
            "turnaround_time": "30 minutes",
            "detects": ["Alcohol intoxication"],
            "price_range": "NPR 300 - 600"
        },
        {
            "name": "Methanol/Ethylene Glycol",
            "description": "Toxic alcohol detection",
            "sample_type": "Blood",
            "turnaround_time": "2-4 hours",
            "detects": ["Methanol poisoning", "Antifreeze poisoning"],
            "clinical_use": "Critical for early diagnosis of toxic alcohol ingestion",
            "price_range": "NPR 1,500 - 3,000"
        },
        {
            "name": "Digoxin Level",
            "description": "Cardiac glycoside measurement",
            "sample_type": "Blood",
            "turnaround_time": "2 hours",
            "detects": ["Digoxin toxicity", "Oleander poisoning"],
            "price_range": "NPR 800 - 1,500"
        }
    ]
    
    return {
        "tests_count": len(tests),
        "tests": tests,
        "data_attribution": {
            "source": "PoisonSense-AI Medical Reference",
            "note": "Prices are approximate and may vary by facility",
            "disclaimer": "Test selection should be guided by clinical presentation"
        }
    }


def _get_standard_tests():
    """Return standard toxicology tests"""
    return [
        {"name": "Blood Toxicology Screen", "price": "NPR 2,500"},
        {"name": "Urine Drug Screen", "price": "NPR 1,000"},
        {"name": "Cholinesterase Level", "price": "NPR 800"},
        {"name": "Acetaminophen Level", "price": "NPR 600"}
    ]
