# Poison schemas - Request/Response models for poison-related endpoints
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PoisonCategoryEnum(str, Enum):
    HOUSEHOLD = "household"
    AGRICULTURAL = "agricultural"
    PHARMACEUTICAL = "pharmaceutical"
    INDUSTRIAL = "industrial"
    NATURAL = "natural"
    FOOD = "food"
    SUBSTANCE_ABUSE = "substance_abuse"


class SeverityEnum(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


# ---------- Request Schemas ----------

class PoisonCreate(BaseModel):
    """Schema for adding a new poison to the knowledge base"""
    name: str = Field(..., min_length=2, max_length=255, description="Poison name")
    common_names: Optional[List[str]] = Field(None, description="Alternative/common names")
    category: PoisonCategoryEnum
    chemical_formula: Optional[str] = None
    common_sources: Optional[List[str]] = None

    # Symptoms
    symptoms_immediate: Optional[List[str]] = Field(None, description="Symptoms within first hour")
    symptoms_delayed: Optional[List[str]] = Field(None, description="Symptoms after 1+ hours")

    # Treatment
    first_aid: Optional[str] = None
    antidote: Optional[str] = None
    antidote_alternatives: Optional[List[str]] = None
    antidote_dosage: Optional[str] = None
    management_protocol: Optional[str] = None
    supportive_care: Optional[str] = None
    contraindications: Optional[str] = None

    # Severity
    typical_severity: Optional[SeverityEnum] = SeverityEnum.MODERATE

    # Monitoring
    tests_required: Optional[List[str]] = None
    monitoring_parameters: Optional[List[str]] = None

    # Prognosis
    prognosis: Optional[str] = None
    recovery_time: Optional[str] = None


class PoisonUpdate(BaseModel):
    """Schema for updating an existing poison record"""
    name: Optional[str] = None
    common_names: Optional[List[str]] = None
    category: Optional[PoisonCategoryEnum] = None
    symptoms_immediate: Optional[List[str]] = None
    symptoms_delayed: Optional[List[str]] = None
    first_aid: Optional[str] = None
    antidote: Optional[str] = None
    antidote_alternatives: Optional[List[str]] = None
    antidote_dosage: Optional[str] = None
    management_protocol: Optional[str] = None
    supportive_care: Optional[str] = None
    contraindications: Optional[str] = None
    typical_severity: Optional[SeverityEnum] = None
    tests_required: Optional[List[str]] = None
    monitoring_parameters: Optional[List[str]] = None
    prognosis: Optional[str] = None
    recovery_time: Optional[str] = None


# ---------- Response Schemas ----------

class AntidoteDetail(BaseModel):
    """Antidote information in response"""
    primary: Optional[str] = None
    alternatives: List[str] = []
    dosage: Optional[str] = None


class ManagementDetail(BaseModel):
    """Management protocol detail"""
    first_aid: Optional[str] = None
    decontamination: Optional[str] = None
    management_protocol: Optional[str] = None
    supportive_care: Optional[str] = None
    contraindications: Optional[str] = None


class DataSourceDetail(BaseModel):
    """Data source attribution for explainability"""
    source: str
    source_type: str = "curated_database"
    last_reviewed: Optional[str] = None
    reviewed_by: Optional[str] = None


class PoisonResponse(BaseModel):
    """Full poison detail response"""
    id: int
    name: str
    common_names: List[str] = []
    category: Optional[str] = None
    typical_severity: Optional[str] = "moderate"
    common_sources: List[str] = []

    symptoms_immediate: List[str] = []
    symptoms_delayed: List[str] = []

    antidote: AntidoteDetail
    management: ManagementDetail

    tests_required: List[str] = []
    monitoring_parameters: List[str] = []

    data_sources: List[DataSourceDetail] = []
    prognosis: Optional[str] = None
    recovery_time: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PoisonListResponse(BaseModel):
    """Paginated list of poisons"""
    count: int
    poisons: List[PoisonResponse]


class PoisonSearchRequest(BaseModel):
    """Search poisons by symptoms or name"""
    query: str = Field(..., min_length=2, description="Search term (symptom or poison name)")
    category: Optional[PoisonCategoryEnum] = None
    severity: Optional[SeverityEnum] = None
    limit: int = Field(10, ge=1, le=50)
