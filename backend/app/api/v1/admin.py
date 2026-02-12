# Admin endpoints for user management
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserProfileResponse
from app.core.security import get_current_active_user
from app.services.email_service import send_approval_email, send_rejection_email
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

class UserApprovalRequest(BaseModel):
    user_id: int
    approved: bool

class PendingUsersResponse(BaseModel):
    total: int
    users: List[UserProfileResponse]

def require_admin(current_user: User = Depends(get_current_active_user)):
    """Dependency to check if user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/users/pending", response_model=PendingUsersResponse)
async def get_pending_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all users pending admin approval
    """
    pending_users = db.query(User).filter(
        User.is_verified == True,
        User.admin_approved == False
    ).order_by(User.created_at.desc()).all()
    
    return PendingUsersResponse(
        total=len(pending_users),
        users=[UserProfileResponse.model_validate(user) for user in pending_users]
    )

@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Approve a user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already approved"
        )
    
    # Approve the user
    user.admin_approved = True
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Send approval notification email
    email_sent, email_msg = await send_approval_email(user.email, user.full_name)
    
    return {
        "message": f"User {user.email} has been approved",
        "email_sent": email_sent,
        "email_message": email_msg,
        "user": UserProfileResponse.model_validate(user)
    }

@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Reject/Delete a user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reject admin users"
        )
    
    email = user.email
    full_name = user.full_name
    
    # Send rejection notification email BEFORE deleting the user
    email_sent, email_msg = await send_rejection_email(email, full_name)
    
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User {email} has been rejected and deleted",
        "email_sent": email_sent,
        "email_message": email_msg
    }

@router.get("/users/all")
async def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all users (for admin dashboard)
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    return {
        "total": len(users),
        "users": [UserProfileResponse.model_validate(user) for user in users]
    }

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get admin dashboard statistics
    """
    total_users = db.query(User).count()
    pending_approval = db.query(User).filter(
        User.is_verified == True,
        User.admin_approved == False
    ).count()
    approved_users = db.query(User).filter(User.admin_approved == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    
    return {
        "total_users": total_users,
        "pending_approval": pending_approval,
        "pending_approvals": pending_approval,  # Frontend compatibility
        "approved_users": approved_users,
        "verified_users": verified_users,
        "unverified_users": total_users - verified_users
    }
