# Users endpoints - Profile management
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, EmergencyContact
from app.schemas.user import (
    UserProfileUpdate, 
    UserProfileResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    ChangePassword
)
from app.core.security import get_current_active_user, get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's full profile with emergency contacts"""
    # Refresh to get relationships
    db.refresh(current_user)
    return UserProfileResponse.model_validate(current_user)

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserProfileResponse.model_validate(current_user)

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

# ============ Emergency Contacts ============

@router.get("/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all emergency contacts for current user"""
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == current_user.id
    ).all()
    return [EmergencyContactResponse.model_validate(c) for c in contacts]

@router.post("/emergency-contacts", response_model=EmergencyContactResponse)
async def add_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new emergency contact"""
    # If this is set as primary, unset other primaries
    if contact_data.is_primary:
        db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    contact = EmergencyContact(
        user_id=current_user.id,
        name=contact_data.name,
        relation_type=contact_data.relationship,
        phone=contact_data.phone,
        email=contact_data.email,
        is_primary=contact_data.is_primary
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return EmergencyContactResponse.model_validate(contact)

@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: int,
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an emergency contact"""
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found"
        )
    
    # If setting as primary, unset others
    if contact_data.is_primary and not contact.is_primary:
        db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    # Update fields
    contact.name = contact_data.name
    contact.relation_type = contact_data.relationship
    contact.phone = contact_data.phone
    contact.email = contact_data.email
    contact.is_primary = contact_data.is_primary
    
    db.commit()
    db.refresh(contact)
    
    return EmergencyContactResponse.model_validate(contact)

@router.delete("/emergency-contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an emergency contact"""
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Emergency contact deleted successfully"}
