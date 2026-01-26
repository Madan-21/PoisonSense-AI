# Control centers - Poison Control Centers API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.poison_center import PoisonCenter, AntidoteInventory
from app.services.location_service import LocationService

router = APIRouter(prefix="/poison-centers", tags=["Poison Centers"])

@router.get("/nearby")
async def get_nearby_poison_centers(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius_km: float = Query(100, description="Search radius in km"),
    limit: int = Query(5, le=20),
    db: Session = Depends(get_db)
):
    """Find poison control centers near user location"""
    service = LocationService(db)
    
    centers = service.find_nearby_poison_centers(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    
    return {
        "count": len(centers),
        "radius_km": radius_km,
        "centers": centers
    }

@router.get("/")
async def list_poison_centers(
    city: Optional[str] = None,
    is_24_hours: Optional[bool] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List all poison control centers"""
    query = db.query(PoisonCenter).filter(PoisonCenter.is_active == True)
    
    if city:
        query = query.filter(PoisonCenter.city.ilike(f"%{city}%"))
    if is_24_hours is not None:
        query = query.filter(PoisonCenter.is_24_hours == is_24_hours)
    
    centers = query.limit(limit).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "phone_primary": c.phone_primary,
            "phone_secondary": c.phone_secondary,
            "toll_free_number": c.toll_free_number,
            "address": c.address,
            "city": c.city,
            "is_24_hours": c.is_24_hours,
            "is_verified": c.is_verified,
            "government_affiliated": c.government_affiliated,
            "services": c.services,
            "latitude": c.latitude,
            "longitude": c.longitude
        }
        for c in centers
    ]

@router.get("/{center_id}")
async def get_poison_center_details(
    center_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed poison center information"""
    center = db.query(PoisonCenter).filter(PoisonCenter.id == center_id).first()
    
    if not center:
        raise HTTPException(status_code=404, detail="Poison center not found")
    
    return {
        "id": center.id,
        "name": center.name,
        "code": center.code,
        "phone_primary": center.phone_primary,
        "phone_secondary": center.phone_secondary,
        "toll_free_number": center.toll_free_number,
        "email": center.email,
        "website": center.website,
        "address": center.address,
        "city": center.city,
        "state": center.state,
        "country": center.country,
        "latitude": center.latitude,
        "longitude": center.longitude,
        "coverage_area": center.coverage_area,
        "coverage_districts": center.coverage_districts,
        "services": center.services,
        "specializations": center.specializations,
        "antidotes_available": center.antidotes_available,
        "is_24_hours": center.is_24_hours,
        "operating_hours": center.operating_hours,
        "is_verified": center.is_verified,
        "government_affiliated": center.government_affiliated
    }

# ============ Antidote Availability ============

@router.get("/antidotes/search")
async def search_antidote_availability(
    antidote_name: str = Query(..., description="Antidote name to search"),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: float = Query(100),
    db: Session = Depends(get_db)
):
    """Search for antidote availability across hospitals and poison centers"""
    service = LocationService(db)
    
    locations = service.find_antidote_locations(
        antidote_name=antidote_name,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    
    return {
        "antidote_searched": antidote_name,
        "count": len(locations),
        "locations": locations
    }

@router.get("/antidotes/all")
async def list_all_antidotes(
    db: Session = Depends(get_db)
):
    """List all unique antidotes in the inventory"""
    inventories = db.query(AntidoteInventory).filter(
        AntidoteInventory.is_available == True
    ).all()
    
    # Get unique antidotes
    antidotes = {}
    for inv in inventories:
        if inv.antidote_name not in antidotes:
            antidotes[inv.antidote_name] = {
                "name": inv.antidote_name,
                "generic_name": inv.generic_name,
                "effective_for": inv.effective_for or [],
                "available_at_count": 0
            }
        antidotes[inv.antidote_name]["available_at_count"] += 1
    
    return list(antidotes.values())
