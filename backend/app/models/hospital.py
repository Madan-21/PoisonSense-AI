# Hospital model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class HospitalType(str, enum.Enum):
    GOVERNMENT = "government"
    PRIVATE = "private"
    COMMUNITY = "community"
    TEACHING = "teaching"

class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    hospital_type = Column(Enum(HospitalType), default=HospitalType.GOVERNMENT)
    registration_number = Column(String(100), unique=True)
    
    # Contact
    phone = Column(String(50), nullable=False)
    emergency_phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    
    # Location
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), default="Nepal")
    pincode = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Facilities - JSON arrays
    facilities = Column(JSON)  # ["ICU", "Emergency", "Toxicology Lab"]
    antidotes_available = Column(JSON)  # List of antidotes available
    toxicology_tests = Column(JSON)  # List of toxicology tests available
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer)
    verified_at = Column(DateTime)
    
    # Operating hours
    is_24_hours = Column(Boolean, default=False)
    operating_hours = Column(Text)  # JSON for operating hours
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctors = relationship("Doctor", back_populates="hospital")
    labs = relationship("ToxicologyLab", back_populates="hospital")


class ToxicologyLab(Base):
    """Labs within hospitals that can conduct toxicology tests"""
    __tablename__ = "toxicology_labs"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"))
    
    name = Column(String(255), nullable=False)
    
    # Tests available - with details
    tests_available = Column(JSON)  # [{"name": "Blood Toxicology", "price": 1500, "duration": "2 hours"}]
    
    # Contact
    phone = Column(String(50))
    email = Column(String(255))
    
    # Operating hours
    operating_hours = Column(Text)
    is_24_hours = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    hospital = relationship("Hospital", back_populates="labs")
