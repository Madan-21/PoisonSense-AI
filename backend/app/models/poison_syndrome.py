# Poison Syndrome Model - Toxidrome Database
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime
from datetime import datetime
from app.db.base import Base

class PoisonSyndrome(Base):
    """
    Toxidrome/Poison Syndrome Database
    Based on clinical presentation patterns for poison identification
    """
    __tablename__ = "poison_syndromes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Syndrome Information
    name = Column(String(255), nullable=False, unique=True)  # e.g., "Sympathomimetic", "Anticholinergic"
    description = Column(Text)
    
    # Associated Agents/Substances
    common_agents = Column(JSON)  # List of substances causing this syndrome
    
    # Clinical Presentation
    mental_status = Column(JSON)  # ["Hypervigilance", "Agitation", "Delirium", etc.]
    vital_signs = Column(JSON)  # {"temperature": "increased/decreased", "heart_rate": "increased", etc.}
    pupils = Column(JSON)  # {"size": "dilated/constricted", "reactivity": "normal/sluggish"}
    skin = Column(JSON)  # {"moisture": "dry/flushed", "temperature": "hot/cold", "color": "pale/red"}
    
    # Other Clinical Features
    other_features = Column(JSON)  # Other distinguishing features
    
    # Treatment Approach
    treatment_priorities = Column(JSON)  # Priority interventions
    specific_antidotes = Column(JSON)  # Antidotes if available
    supportive_care = Column(Text)  # General supportive care measures
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
