# User model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL_ADMIN = "hospital_admin"
    POISON_CENTER_ADMIN = "poison_center_admin"
    BLOG_REVIEWER = "blog_reviewer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    
    # Profile info
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    blood_group = Column(String(10))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="Nepal")
    
    # Medical info
    allergies = Column(Text)  # JSON string
    medical_conditions = Column(Text)  # JSON string
    current_medications = Column(Text)  # JSON string
    
    # Professional registration (for doctors/hospitals during signup)
    registration_number = Column(String(100))  # Medical license or hospital registration number
    license_document = Column(String(500))  # Path to uploaded license document
    specialization = Column(String(255))  # Doctor specialization or hospital department
    experience_years = Column(Integer)  # Doctor experience years
    hospital_address = Column(Text)  # Hospital address (for hospital_admin)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    admin_approved = Column(Boolean, default=False)  # Requires admin approval after email verification
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    analysis_history = relationship("AnalysisLog", back_populates="user", cascade="all, delete-orphan")
    
    # For doctors - specify foreign key to avoid ambiguity
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False, foreign_keys="[Doctor.user_id]")


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    relation_type = Column(String(100))  # Renamed to avoid conflict with relationship()
    phone = Column(String(20), nullable=False)
    email = Column(String(255))
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to User
    user = relationship("User", back_populates="emergency_contacts")