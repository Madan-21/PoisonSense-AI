# ML Data Module - RAG Data Sources for PoisonSense AI
"""
This module provides structured data for the RAG (Retrieval-Augmented Generation) system.

Data Sources:
1. comprehensive_toxicology_data - Detailed poison information from medical sources
2. poison_knowledge - Structured poison entries for RAG retrieval
3. nepal_facilities - Hospital, lab, and poison center directory for Nepal
"""

from .comprehensive_toxicology_data import (
    COMPREHENSIVE_POISONS,
    SYMPTOM_POISON_MAPPING,
    EMERGENCY_NUMBERS,
    get_poison_by_symptoms,
    get_poison_details,
    get_antidote_info,
    get_first_aid,
    get_management_protocol
)

from .poison_knowledge import (
    POISON_KNOWLEDGE,
    retrieve_poison_by_name,
    retrieve_poison_by_symptoms,
    retrieve_poison_by_category,
    get_poison_safety_info,
    get_antidote_info as get_rag_antidote_info,
    get_emergency_signs
)

from .nepal_facilities import (
    NEPAL_FACILITIES,
    FacilityType,
    retrieve_nearest_facilities,
    retrieve_facilities_by_antidote,
    retrieve_facilities_by_service,
    get_poison_control_hotline,
    get_facility_details
)
