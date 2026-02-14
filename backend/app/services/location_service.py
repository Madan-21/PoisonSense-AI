# Location service - Finding nearby hospitals, poison centers, antidote availability
from typing import Dict, List, Optional, Tuple
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.hospital import Hospital, ToxicologyLab
from app.models.poison_center import PoisonCenter, AntidoteInventory

class LocationService:
    """Service for location-based queries and distance calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_distance(
        self, 
        lat1: float, lon1: float, 
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def find_nearby_hospitals(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
        limit: int = 10,
        has_toxicology_lab: bool = False,
        antidote_name: Optional[str] = None
    ) -> List[Dict]:
        """Find hospitals near given coordinates"""
        
        # Get all active hospitals with coordinates
        query = self.db.query(Hospital).filter(
            and_(
                Hospital.is_active == True,
                Hospital.latitude.isnot(None),
                Hospital.longitude.isnot(None)
            )
        )
        
        if has_toxicology_lab:
            query = query.join(ToxicologyLab).filter(ToxicologyLab.is_active == True)
        
        hospitals = query.all()
        
        # Calculate distances and filter
        results = []
        for hospital in hospitals:
            distance = self.calculate_distance(
                latitude, longitude,
                hospital.latitude, hospital.longitude
            )
            
            if distance <= radius_km:
                # Check antidote availability
                has_antidote = False
                if antidote_name:
                    antidote = self.db.query(AntidoteInventory).filter(
                        and_(
                            AntidoteInventory.hospital_id == hospital.id,
                            AntidoteInventory.antidote_name.ilike(f"%{antidote_name}%"),
                            AntidoteInventory.is_available == True
                        )
                    ).first()
                    has_antidote = antidote is not None
                
                results.append({
                    "id": hospital.id,
                    "name": hospital.name,
                    "type": "hospital",
                    "hospital_type": hospital.hospital_type.value if hospital.hospital_type else None,
                    "distance_km": round(distance, 2),
                    "phone": hospital.phone,
                    "emergency_phone": hospital.emergency_phone,
                    "address": hospital.address,
                    "city": hospital.city,
                    "state": hospital.state,
                    "country": hospital.country,
                    "is_24_hours": hospital.is_24_hours,
                    "has_antidote": has_antidote,
                    "is_verified": hospital.is_verified,
                    "latitude": float(hospital.latitude) if hospital.latitude else None,
                    "longitude": float(hospital.longitude) if hospital.longitude else None,
                    "facilities": hospital.facilities or [],
                    "antidotes_available": hospital.antidotes_available or [],
                    "toxicology_tests": hospital.toxicology_tests or []
                })
        
        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]
    
    def find_nearby_poison_centers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        limit: int = 5
    ) -> List[Dict]:
        """Find poison control centers near given coordinates"""
        
        centers = self.db.query(PoisonCenter).filter(
            and_(
                PoisonCenter.is_active == True,
                PoisonCenter.latitude.isnot(None),
                PoisonCenter.longitude.isnot(None)
            )
        ).all()
        
        results = []
        for center in centers:
            distance = self.calculate_distance(
                latitude, longitude,
                center.latitude, center.longitude
            )
            
            if distance <= radius_km:
                results.append({
                    "id": center.id,
                    "name": center.name,
                    "type": "poison_center",
                    "distance_km": round(distance, 2),
                    "phone_primary": center.phone_primary,
                    "phone": center.phone_primary,  # Also include as 'phone' for consistency
                    "phone_secondary": center.phone_secondary,
                    "toll_free_number": center.toll_free_number,
                    "address": center.address,
                    "city": center.city,
                    "state": center.state,
                    "country": center.country,
                    "is_24_hours": center.is_24_hours,
                    "is_verified": center.is_verified,
                    "government_affiliated": center.government_affiliated,
                    "latitude": float(center.latitude) if center.latitude else None,
                    "longitude": float(center.longitude) if center.longitude else None,
                    "services": center.services or [],
                    "antidotes_available": center.antidotes_available or []
                })
        
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]
    
    def find_antidote_locations(
        self,
        antidote_name: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 100
    ) -> List[Dict]:
        """Find locations where a specific antidote is available"""
        
        query = self.db.query(AntidoteInventory).filter(
            and_(
                AntidoteInventory.antidote_name.ilike(f"%{antidote_name}%"),
                AntidoteInventory.is_available == True,
                AntidoteInventory.quantity_available > 0
            )
        )
        
        inventories = query.all()
        results = []
        
        for inv in inventories:
            location_info = None
            location_type = None
            
            if inv.hospital_id:
                hospital = self.db.query(Hospital).filter(Hospital.id == inv.hospital_id).first()
                if hospital:
                    location_info = hospital
                    location_type = "hospital"
            elif inv.poison_center_id:
                center = self.db.query(PoisonCenter).filter(PoisonCenter.id == inv.poison_center_id).first()
                if center:
                    location_info = center
                    location_type = "poison_center"
            
            if location_info:
                distance = None
                if latitude and longitude and location_info.latitude and location_info.longitude:
                    distance = self.calculate_distance(
                        latitude, longitude,
                        location_info.latitude, location_info.longitude
                    )
                    if distance > radius_km:
                        continue
                
                results.append({
                    "antidote_name": inv.antidote_name,
                    "generic_name": inv.generic_name,
                    "quantity_available": inv.quantity_available,
                    "unit": inv.unit,
                    "location_type": location_type,
                    "location_name": location_info.name,
                    "phone": location_info.phone if location_type == "hospital" else location_info.phone_primary,
                    "address": location_info.address,
                    "city": location_info.city,
                    "distance_km": round(distance, 2) if distance else None,
                    "latitude": location_info.latitude,
                    "longitude": location_info.longitude
                })
        
        if latitude and longitude:
            results.sort(key=lambda x: x["distance_km"] or 9999)
        
        return results
    
    def find_toxicology_labs(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        test_name: Optional[str] = None,
        radius_km: float = 50
    ) -> List[Dict]:
        """Find toxicology labs, optionally filtered by test availability"""
        
        query = self.db.query(ToxicologyLab).join(Hospital).filter(
            and_(
                ToxicologyLab.is_active == True,
                Hospital.is_active == True
            )
        )
        
        labs = query.all()
        results = []
        
        for lab in labs:
            hospital = lab.hospital
            
            # Filter by test name if specified
            if test_name and lab.tests_available:
                tests = lab.tests_available
                if not any(test_name.lower() in str(t).lower() for t in tests):
                    continue
            
            distance = None
            if latitude and longitude and hospital.latitude and hospital.longitude:
                distance = self.calculate_distance(
                    latitude, longitude,
                    hospital.latitude, hospital.longitude
                )
                if distance > radius_km:
                    continue
            
            results.append({
                "lab_id": lab.id,
                "lab_name": lab.name,
                "hospital_id": hospital.id,
                "hospital_name": hospital.name,
                "tests_available": lab.tests_available or [],
                "phone": lab.phone or hospital.phone,
                "address": hospital.address,
                "city": hospital.city,
                "is_24_hours": lab.is_24_hours,
                "distance_km": round(distance, 2) if distance else None,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude
            })
        
        if latitude and longitude:
            results.sort(key=lambda x: x["distance_km"] or 9999)
        
        return results
