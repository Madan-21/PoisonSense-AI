# Hospitals endpoints
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.models.hospital import Hospital, ToxicologyLab
from app.models.user import User
from app.models.ai_log import AnalysisLog
from app.services.location_service import LocationService
from app.core.security import get_current_user_required

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
            "state": h.state,
            "is_24_hours": h.is_24_hours,
            "is_verified": h.is_verified,
            "facilities": h.facilities or [],
            "antidotes_available": h.antidotes_available or [],
            "toxicology_tests": h.toxicology_tests or [],
            "latitude": h.latitude,
            "longitude": h.longitude
        }
        for h in hospitals
    ]


# ─── Hospital Admin Endpoints ─────────────────────────────────────────────────
# NOTE: These MUST be defined BEFORE /{hospital_id} to avoid path conflicts.


class HospitalUpdateSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    emergency_phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_24_hours: Optional[bool] = None
    operating_hours: Optional[str] = None
    facilities: Optional[List[str]] = None
    antidotes_available: Optional[List[str]] = None
    toxicology_tests: Optional[List[Any]] = None


def _get_admin_hospital(db: Session, current_user: User) -> Hospital:
    """Helper: get the hospital managed by the current admin user."""
    if current_user.role != "hospital_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hospital admin privileges required")
    hospital = db.query(Hospital).filter(Hospital.admin_id == current_user.id).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hospital associated with this account")
    return hospital


@router.get("/my-hospital")
async def get_my_hospital(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get full hospital details for the current admin."""
    hospital = _get_admin_hospital(db, current_user)
    return {
        "id": hospital.id,
        "name": hospital.name,
        "type": hospital.hospital_type.value if hospital.hospital_type else None,
        "registration_number": hospital.registration_number,
        "phone": hospital.phone or "",
        "emergency_phone": hospital.emergency_phone or "",
        "email": hospital.email or "",
        "website": hospital.website or "",
        "address": hospital.address or "",
        "city": hospital.city or "",
        "state": hospital.state or "",
        "is_24_hours": hospital.is_24_hours or False,
        "operating_hours": hospital.operating_hours or "",
        "facilities": hospital.facilities or [],
        "antidotes_available": hospital.antidotes_available or [],
        "toxicology_tests": hospital.toxicology_tests or [],
        "is_verified": hospital.is_verified,
        "latitude": hospital.latitude,
        "longitude": hospital.longitude,
    }


@router.put("/my-hospital")
async def update_my_hospital(
    payload: HospitalUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Update hospital information (hospital admin only)."""
    hospital = _get_admin_hospital(db, current_user)

    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            setattr(hospital, field, value)
    hospital.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hospital)
    return {"message": "Hospital updated successfully", "hospital_id": hospital.id}


@router.get("/my-hospital/inventory")
async def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get the antidote inventory for the current admin's hospital."""
    hospital = _get_admin_hospital(db, current_user)
    return {
        "hospital_id": hospital.id,
        "hospital_name": hospital.name,
        "antidotes_available": hospital.antidotes_available or [],
        "toxicology_tests": hospital.toxicology_tests or [],
        "facilities": hospital.facilities or [],
    }


@router.put("/my-hospital/inventory")
async def update_inventory(
    antidotes: Optional[List[str]] = Body(None),
    toxicology_tests: Optional[List[Any]] = Body(None),
    facilities: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Update antidotes / tests / facilities inventory."""
    hospital = _get_admin_hospital(db, current_user)

    if antidotes is not None:
        hospital.antidotes_available = antidotes
    if toxicology_tests is not None:
        hospital.toxicology_tests = toxicology_tests
    if facilities is not None:
        hospital.facilities = facilities
    hospital.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hospital)
    return {
        "message": "Inventory updated successfully",
        "antidotes_available": hospital.antidotes_available or [],
        "toxicology_tests": hospital.toxicology_tests or [],
        "facilities": hospital.facilities or [],
    }


@router.get("/my-hospital/reports")
async def get_reports(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get case reports and statistics for the hospital."""
    hospital = _get_admin_hospital(db, current_user)

    since = datetime.utcnow() - timedelta(days=days)

    total_cases = db.query(AnalysisLog).filter(AnalysisLog.hospital_referred == True).count()

    recent_cases = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.hospital_referred == True, AnalysisLog.created_at >= since)
        .order_by(AnalysisLog.created_at.desc())
        .all()
    )

    # Severity breakdown
    severity_counts: Dict[str, int] = {}
    poison_counts: Dict[str, int] = {}
    for c in recent_cases:
        sev = c.severity_assessment or "unknown"
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        poison = c.predicted_poison or "unknown"
        poison_counts[poison] = poison_counts.get(poison, 0) + 1

    # Top 10 poisons
    top_poisons = sorted(poison_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "hospital_name": hospital.name,
        "period_days": days,
        "total_cases_all_time": total_cases,
        "cases_in_period": len(recent_cases),
        "severity_breakdown": severity_counts,
        "top_poisons": [{"name": p, "count": c} for p, c in top_poisons],
        "recent_cases": [
            {
                "id": c.id,
                "predicted_poison": c.predicted_poison,
                "severity": c.severity_assessment,
                "antidote": c.antidote_suggested,
                "date": c.created_at.isoformat(),
            }
            for c in recent_cases[:20]
        ],
    }


# ─── Public Detail Endpoints ──────────────────────────────────────────────────


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
