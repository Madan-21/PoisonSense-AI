# Doctor verification - Doctors API with credential verification
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.models.doctor import Doctor, VerificationStatus
from app.models.user import User, UserRole
from app.core.security import get_current_user, require_role, get_password_hash
from app.services.location_service import LocationService

router = APIRouter(prefix="/doctors", tags=["Doctors"])

# ============ Schemas ============

class DoctorRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    license_number: str
    medical_council: str
    specialization: str
    institution: str
    institution_address: Optional[str] = None
    years_of_experience: Optional[int] = None
    qualification: Optional[str] = None

class DoctorVerificationRequest(BaseModel):
    status: VerificationStatus
    verification_notes: Optional[str] = None

class DoctorUpdateRequest(BaseModel):
    phone: Optional[str] = None
    specialization: Optional[str] = None
    institution: Optional[str] = None
    institution_address: Optional[str] = None
    years_of_experience: Optional[int] = None
    is_available_consultation: Optional[bool] = None
    consultation_hours: Optional[str] = None

# ============ Doctor Registration ============

@router.post("/register")
async def register_doctor(
    request: DoctorRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new doctor - requires credential verification"""
    # Check if email exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if license number exists
    existing_license = db.query(Doctor).filter(
        Doctor.license_number == request.license_number
    ).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already registered")
    
    # Create user account
    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        phone=request.phone,
        role=UserRole.DOCTOR
    )
    db.add(user)
    db.flush()  # Get user ID
    
    # Create doctor profile (pending verification)
    doctor = Doctor(
        user_id=user.id,
        license_number=request.license_number,
        medical_council=request.medical_council,
        specialization=request.specialization,
        institution=request.institution,
        institution_address=request.institution_address,
        years_of_experience=request.years_of_experience,
        qualification=request.qualification,
        verification_status=VerificationStatus.PENDING
    )
    db.add(doctor)
    db.commit()
    
    return {
        "message": "Doctor registration submitted successfully",
        "status": "pending_verification",
        "doctor_id": doctor.id,
        "note": "Your credentials will be verified within 24-48 hours. You will receive an email once verified."
    }

# ============ Doctor Verification (Admin Only) ============

@router.put("/{doctor_id}/verify")
async def verify_doctor(
    doctor_id: int,
    request: DoctorVerificationRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Admin: Verify or reject a doctor's credentials"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.verification_status = request.status
    doctor.verification_notes = request.verification_notes
    
    if request.status == VerificationStatus.VERIFIED:
        doctor.is_verified = True
    elif request.status == VerificationStatus.REJECTED:
        doctor.is_verified = False
    
    db.commit()
    
    return {
        "message": f"Doctor verification status updated to {request.status.value}",
        "doctor_id": doctor_id
    }

@router.get("/pending-verification")
async def get_pending_verifications(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Admin: List doctors pending verification"""
    doctors = db.query(Doctor).filter(
        Doctor.verification_status == VerificationStatus.PENDING
    ).all()
    
    return [
        {
            "id": d.id,
            "user_id": d.user_id,
            "license_number": d.license_number,
            "medical_council": d.medical_council,
            "specialization": d.specialization,
            "institution": d.institution,
            "qualification": d.qualification,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in doctors
    ]

# ============ Public Doctor Search ============

@router.get("/")
async def list_verified_doctors(
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    available_now: bool = False,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List verified doctors available for consultation"""
    query = db.query(Doctor).filter(
        Doctor.is_verified == True,
        Doctor.is_active == True
    )
    
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if available_now:
        query = query.filter(Doctor.is_available_consultation == True)
    
    doctors = query.limit(limit).all()
    
    result = []
    for d in doctors:
        # Get user info
        user = db.query(User).filter(User.id == d.user_id).first()
        result.append({
            "id": d.id,
            "name": user.full_name if user else "Unknown",
            "specialization": d.specialization,
            "institution": d.institution,
            "years_of_experience": d.years_of_experience,
            "qualification": d.qualification,
            "is_available_consultation": d.is_available_consultation,
            "consultation_hours": d.consultation_hours,
            "rating": d.rating,
            "total_consultations": d.total_consultations
        })
    
    return result

@router.get("/{doctor_id}")
async def get_doctor_details(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed doctor information"""
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_verified == True
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    user = db.query(User).filter(User.id == doctor.user_id).first()
    
    return {
        "id": doctor.id,
        "name": user.full_name if user else "Unknown",
        "email": user.email if user else None,
        "phone": user.phone if user else None,
        "specialization": doctor.specialization,
        "qualification": doctor.qualification,
        "institution": doctor.institution,
        "institution_address": doctor.institution_address,
        "years_of_experience": doctor.years_of_experience,
        "medical_council": doctor.medical_council,
        "is_available_consultation": doctor.is_available_consultation,
        "consultation_hours": doctor.consultation_hours,
        "rating": doctor.rating,
        "total_consultations": doctor.total_consultations,
        "is_verified": doctor.is_verified
    }

# ============ Doctor Profile Management ============

@router.get("/me/profile")
async def get_my_doctor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current doctor's profile"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Not a doctor account")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    return {
        "id": doctor.id,
        "license_number": doctor.license_number,
        "medical_council": doctor.medical_council,
        "specialization": doctor.specialization,
        "institution": doctor.institution,
        "institution_address": doctor.institution_address,
        "years_of_experience": doctor.years_of_experience,
        "qualification": doctor.qualification,
        "verification_status": doctor.verification_status.value,
        "is_verified": doctor.is_verified,
        "is_available_consultation": doctor.is_available_consultation,
        "consultation_hours": doctor.consultation_hours,
        "rating": doctor.rating,
        "total_consultations": doctor.total_consultations
    }

@router.put("/me/profile")
async def update_my_doctor_profile(
    request: DoctorUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update doctor's profile"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Not a doctor account")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(doctor, field, value)
    
    db.commit()
    
    return {"message": "Profile updated successfully"}
