# Doctor model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Professional info
    registration_number = Column(String(100), unique=True, nullable=False)  # Medical council registration
    specialization = Column(String(255), nullable=False)  # e.g., "Toxicology", "Emergency Medicine"
    qualification = Column(String(255), nullable=False)  # e.g., "MBBS, MD"
    experience_years = Column(Integer)
    
    # Verification - CRITICAL for trust
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verification_document = Column(String(500))  # Path to uploaded document
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    
    # Affiliation
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    poison_center_id = Column(Integer, ForeignKey("poison_centers.id"))
    
    # Contact
    clinic_address = Column(Text)
    consultation_fee = Column(Float)
    available_hours = Column(Text)  # JSON string for availability
    
    # Location for nearby search
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Status
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile", foreign_keys=[user_id])
    hospital = relationship("Hospital", back_populates="doctors")
    poison_center = relationship("PoisonCenter", back_populates="doctors")
