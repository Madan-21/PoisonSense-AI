# Hospitals endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.hospital import Hospital, ToxicologyLab
from app.services.location_service import LocationService

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

@router.get("/nearby")
async def get_nearby_hospitals(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(50, description="Search radius in km"),
    has_toxicology_lab: bool = Query(False),
    antidote: Optional[str] = Query(None, description="Filter by antidote availability"),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Find hospitals near user location"""
    service = LocationService(db)
    
    hospitals = service.find_nearby_hospitals(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
        has_toxicology_lab=has_toxicology_lab,
        antidote_name=antidote
    )
    
    return {
        "count": len(hospitals),
        "radius_km": radius_km,
        "hospitals": hospitals
    }

@router.get("/")
async def list_hospitals(
    city: Optional[str] = None,
    is_24_hours: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List all hospitals with optional filters"""
    query = db.query(Hospital).filter(Hospital.is_active == True)
    
    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))
    if is_24_hours is not None:
        query = query.filter(Hospital.is_24_hours == is_24_hours)
    if is_verified is not None:
        query = query.filter(Hospital.is_verified == is_verified)
    
    hospitals = query.limit(limit).all()
    
    return [
        {
            "id": h.id,
            "name": h.name,
            "type": h.hospital_type.value if h.hospital_type else None,
            "phone": h.phone,
            "emergency_phone": h.emergency_phone,
            "address": h.address,
            "city": h.city,
            "is_24_hours": h.is_24_hours,
            "is_verified": h.is_verified,
            "facilities": h.facilities,
            "latitude": h.latitude,
            "longitude": h.longitude
        }
        for h in hospitals
    ]

@router.get("/{hospital_id}")
async def get_hospital_details(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed hospital information"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get labs
    labs = db.query(ToxicologyLab).filter(
        ToxicologyLab.hospital_id == hospital_id,
        ToxicologyLab.is_active == True
    ).all()
    
    return {
        "id": hospital.id,
        "name": hospital.name,
        "type": hospital.hospital_type.value if hospital.hospital_type else None,
        "registration_number": hospital.registration_number,
        "phone": hospital.phone,
        "emergency_phone": hospital.emergency_phone,
        "email": hospital.email,
        "website": hospital.website,
        "address": hospital.address,
        "city": hospital.city,
        "state": hospital.state,
        "country": hospital.country,
        "latitude": hospital.latitude,
        "longitude": hospital.longitude,
        "is_24_hours": hospital.is_24_hours,
        "operating_hours": hospital.operating_hours,
        "facilities": hospital.facilities,
        "antidotes_available": hospital.antidotes_available,
        "toxicology_tests": hospital.toxicology_tests,
        "is_verified": hospital.is_verified,
        "toxicology_labs": [
            {
                "id": lab.id,
                "name": lab.name,
                "tests_available": lab.tests_available,
                "phone": lab.phone,
                "is_24_hours": lab.is_24_hours
            }
            for lab in labs
        ]
    }

@router.get("/labs/nearby")
async def get_nearby_toxicology_labs(
    latitude: float = Query(...),
    longitude: float = Query(...),
    test_name: Optional[str] = Query(None, description="Filter by specific test"),
    radius_km: float = Query(50),
    db: Session = Depends(get_db)
):
    """Find toxicology labs near user location"""
    service = LocationService(db)
    
    labs = service.find_toxicology_labs(
        latitude=latitude,
        longitude=longitude,
        test_name=test_name,
        radius_km=radius_km
    )
    
    return {
        "count": len(labs),
        "labs": labs
    }
