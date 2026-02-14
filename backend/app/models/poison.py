# Poison model - Medical Knowledge Database
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class PoisonCategory(str, enum.Enum):
    HOUSEHOLD = "household"
    AGRICULTURAL = "agricultural"
    PHARMACEUTICAL = "pharmaceutical"
    INDUSTRIAL = "industrial"
    NATURAL = "natural"  # Plants, animals, fungi
    FOOD = "food"
    SUBSTANCE_ABUSE = "substance_abuse"

class SeverityLevel(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class Poison(Base):
    """Comprehensive poison database - the medical knowledge base"""
    __tablename__ = "poisons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    name = Column(String(255), nullable=False, unique=True)
    common_names = Column(JSON)  # List of alternative names
    category = Column(Enum(PoisonCategory), nullable=False)
    
    # Chemical info
    chemical_formula = Column(String(100))
    cas_number = Column(String(50))  # Chemical Abstracts Service number
    
    # Sources - Where it's found
    common_sources = Column(JSON)  # ["Rat poison", "Pesticides", "Household cleaners"]
    
    # Symptoms
    symptoms_immediate = Column(JSON)  # Symptoms within first hour
    symptoms_delayed = Column(JSON)  # Symptoms after 1+ hours
    symptoms_by_system = Column(JSON)  # Organized by body system
    
    # Severity
    typical_severity = Column(Enum(SeverityLevel), default=SeverityLevel.MODERATE)
    lethal_dose = Column(String(255))  # If known
    
    # Treatment - CRITICAL MEDICAL INFO
    first_aid = Column(Text)  # Immediate steps
    decontamination = Column(Text)  # How to remove poison
    antidote = Column(String(255))  # Primary antidote
    antidote_alternatives = Column(JSON)  # Alternative antidotes
    antidote_dosage = Column(Text)  # Dosage information
    
    # Management Protocol
    management_protocol = Column(Text)  # Full treatment protocol
    supportive_care = Column(Text)  # Supportive care measures
    contraindications = Column(Text)  # What NOT to do
    
    # Monitoring
    tests_required = Column(JSON)  # Lab tests needed
    monitoring_parameters = Column(JSON)  # What to monitor
    
    # Prognosis
    prognosis = Column(Text)
    recovery_time = Column(String(255))
    
    # References - EXPLAINABILITY
    data_sources = Column(JSON)  # Where this info came from
    last_reviewed = Column(DateTime)
    reviewed_by = Column(String(255))  # Medical professional who reviewed
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ManagementProtocol(Base):
    """Detailed management protocols for poisoning cases"""
    __tablename__ = "management_protocols"
    
    id = Column(Integer, primary_key=True, index=True)
    poison_id = Column(Integer, ForeignKey("poisons.id", ondelete="CASCADE"))
    
    # Protocol details
    title = Column(String(255), nullable=False)
    severity_level = Column(Enum(SeverityLevel))
    
    # Steps
    immediate_actions = Column(JSON)  # Step-by-step immediate actions
    hospital_care = Column(JSON)  # Hospital-level care
    icu_care = Column(JSON)  # ICU-level care if needed
    
    # Special considerations
    pediatric_considerations = Column(Text)
    pregnancy_considerations = Column(Text)
    elderly_considerations = Column(Text)
    
    # Timeline
    expected_timeline = Column(Text)
    follow_up_required = Column(Text)
    
    # References
    source = Column(String(255))  # e.g., "WHO Guidelines 2024"
    source_url = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
