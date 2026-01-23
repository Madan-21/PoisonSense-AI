# Poison center model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PoisonCenter(Base):
    """Poison Control Centers - Primary resource for poison emergencies"""
    __tablename__ = "poison_centers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)  # e.g., "NPCC-KTM-001"
    
    # Contact - CRITICAL
    phone_primary = Column(String(50), nullable=False)
    phone_secondary = Column(String(50))
    toll_free_number = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    
    # Location
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), default="Nepal")
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Coverage area
    coverage_area = Column(Text)  # Description of areas covered
    coverage_districts = Column(JSON)  # List of districts covered
    
    # Services
    services = Column(JSON)  # ["24/7 Hotline", "Toxicology Consultation", "Antidote Info"]
    specializations = Column(JSON)  # Types of poisoning they specialize in
    
    # Antidote inventory
    antidotes_available = Column(JSON)  # List of antidotes stocked
    
    # Verification
    is_verified = Column(Boolean, default=True)  # Government centers are auto-verified
    government_affiliated = Column(Boolean, default=True)
    
    # Operating hours
    is_24_hours = Column(Boolean, default=True)
    operating_hours = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctors = relationship("Doctor", back_populates="poison_center")


class AntidoteInventory(Base):
    """Track antidote availability across centers and hospitals"""
    __tablename__ = "antidote_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location - either hospital or poison center
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    poison_center_id = Column(Integer, ForeignKey("poison_centers.id"))
    
    # Antidote details
    antidote_name = Column(String(255), nullable=False)
    generic_name = Column(String(255))
    brand_names = Column(JSON)  # List of brand names
    
    # For which poisons
    effective_for = Column(JSON)  # List of poisons this antidote treats
    
    # Availability
    quantity_available = Column(Integer, default=0)
    unit = Column(String(50))  # e.g., "vials", "mg", "ml"
    last_restocked = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Status
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
