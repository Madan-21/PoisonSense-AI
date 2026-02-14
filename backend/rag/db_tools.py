"""
Database-backed tools for the RAG agent.
Provides real-time hospital, antidote, and poison center lookups
that the agent can integrate into its answers.
"""

from typing import Dict, Any, List, Optional
from app.db.session import SessionLocal
from app.services.location_service import LocationService


def find_nearby_hospitals_db(
    latitude: float,
    longitude: float,
    radius_km: float = 100,
    limit: int = 5,
    antidote_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Find nearby hospitals from the database using user's coordinates."""
    db = SessionLocal()
    try:
        service = LocationService(db)
        hospitals = service.find_nearby_hospitals(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
            antidote_name=antidote_name,
        )
        return hospitals
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def find_nearby_poison_centers_db(
    latitude: float,
    longitude: float,
    radius_km: float = 200,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Find nearby poison control centers from the database."""
    db = SessionLocal()
    try:
        service = LocationService(db)
        centers = service.find_nearby_poison_centers(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
        )
        return centers
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def search_antidote_availability(
    antidote_name: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 200,
) -> List[Dict[str, Any]]:
    """Search for antidote availability at hospitals/centers."""
    db = SessionLocal()
    try:
        service = LocationService(db)
        results = service.find_antidote_locations(
            antidote_name=antidote_name,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )
        return results
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def get_all_hospitals_summary() -> List[Dict[str, Any]]:
    """Get a summary of all hospitals in the system (no location needed)."""
    db = SessionLocal()
    try:
        from app.models.hospital import Hospital
        hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
        return [
            {
                "id": h.id,
                "name": h.name,
                "phone": h.phone,
                "emergency_phone": h.emergency_phone,
                "address": h.address,
                "city": h.city,
                "state": h.state,
                "country": h.country,
                "is_24_hours": h.is_24_hours,
                "facilities": h.facilities or [],
                "antidotes_available": h.antidotes_available or [],
                "latitude": h.latitude,
                "longitude": h.longitude,
            }
            for h in hospitals
        ]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def get_all_antidotes_summary() -> List[Dict[str, Any]]:
    """Get a summary of all antidotes tracked in the system."""
    db = SessionLocal()
    try:
        from app.models.poison_center import AntidoteInventory
        from app.models.hospital import Hospital
        inventories = (
            db.query(AntidoteInventory)
            .filter(AntidoteInventory.is_available == True)
            .all()
        )
        results = []
        seen = set()
        for inv in inventories:
            hospital = None
            if inv.hospital_id:
                hospital = db.query(Hospital).filter(Hospital.id == inv.hospital_id).first()
            results.append({
                "antidote_name": inv.antidote_name,
                "generic_name": inv.generic_name,
                "effective_for": inv.effective_for or [],
                "quantity_available": inv.quantity_available,
                "location": hospital.name if hospital else "Unknown",
                "city": hospital.city if hospital else "Unknown",
                "phone": hospital.phone if hospital else "",
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def format_hospitals_for_answer(hospitals: List[Dict], user_asked_location: bool = True) -> str:
    """Format hospital list into a readable text block for the LLM answer."""
    if not hospitals:
        return "No hospitals found in the database for the given location."
    
    lines = []
    for i, h in enumerate(hospitals[:5], 1):
        name = h.get("name", "Unknown")
        city = h.get("city", "")
        phone = h.get("emergency_phone") or h.get("phone", "")
        distance = h.get("distance_km")
        is_24h = "✅ 24/7" if h.get("is_24_hours") else ""
        antidotes = h.get("antidotes_available", [])
        antidote_str = ", ".join(antidotes[:5]) if antidotes else "Contact for availability"

        line = f"**{i}. {name}** — {city}"
        if distance is not None:
            line += f" ({distance} km away)"
        line += f"\n   📞 {phone} {is_24h}"
        line += f"\n   📍 {h.get('address', '')}"
        if antidotes:
            line += f"\n   💊 Antidotes: {antidote_str}"
        lines.append(line)
    
    return "\n\n".join(lines)


def format_antidotes_for_answer(antidotes: List[Dict]) -> str:
    """Format antidote availability into a readable text block."""
    if not antidotes:
        return "No antidote availability information found."
    
    lines = []
    for i, a in enumerate(antidotes[:8], 1):
        name = a.get("antidote_name", "Unknown")
        generic = a.get("generic_name", "")
        location = a.get("location", "")
        city = a.get("city", "")
        effective_for = a.get("effective_for", [])
        qty = a.get("quantity_available", 0)
        phone = a.get("phone", "")
        distance = a.get("distance_km")

        line = f"**{i}. {name}**"
        if generic:
            line += f" ({generic})"
        if effective_for:
            line += f"\n   Effective for: {', '.join(effective_for)}"
        line += f"\n   Available at: {location}, {city}"
        if distance is not None:
            line += f" ({distance} km away)"
        if phone:
            line += f"\n   📞 {phone}"
        lines.append(line)
    
    return "\n\n".join(lines)
