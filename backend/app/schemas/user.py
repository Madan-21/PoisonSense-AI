# User schemas
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class EmergencyContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    relationship: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    is_primary: bool = False

class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    relation_type: Optional[str] = Field(None, alias="relation_type")
    phone: str
    email: Optional[str]
    is_primary: bool
    
    # Map relation_type to relationship for frontend
    @property
    def relationship(self) -> Optional[str]:
        return self.relation_type
    
    class Config:
        from_attributes = True
        populate_by_name = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    allergies: Optional[str] = None  # JSON string
    medical_conditions: Optional[str] = None
    current_medications: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    blood_group: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    allergies: Optional[str]
    medical_conditions: Optional[str]
    current_medications: Optional[str]
    registration_number: Optional[str] = None
    license_document: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    hospital_address: Optional[str] = None
    is_active: bool
    is_verified: bool
    admin_approved: Optional[bool] = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    emergency_contacts: List[EmergencyContactResponse] = []
    
    class Config:
        from_attributes = True

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
