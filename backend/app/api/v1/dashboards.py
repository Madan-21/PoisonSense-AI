# Role-Based Dashboard API Endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.hospital import Hospital
from app.models.doctor import Doctor
from app.models.blog_submission import BlogSubmission
from app.models.ai_log import AnalysisLog
from app.core.security import get_current_user_required

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


@router.get("/doctor")
async def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Doctor Dashboard - Shows cases, blog submissions, patients
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required"
        )
    
    # Get doctor info
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    
    # Get doctor's blog submissions
    my_blogs = db.query(BlogSubmission).filter(
        BlogSubmission.author_id == current_user.id
    ).count()
    
    pending_blogs = db.query(BlogSubmission).filter(
        BlogSubmission.author_id == current_user.id,
        BlogSubmission.status == "pending"
    ).count()
    
    approved_blogs = db.query(BlogSubmission).filter(
        BlogSubmission.author_id == current_user.id,
        BlogSubmission.status == "approved"
    ).count()
    
    # Get recent AI logs (cases consulted)
    recent_cases = db.query(AnalysisLog).filter(
        AnalysisLog.doctor_consulted == True
    ).order_by(AnalysisLog.created_at.desc()).limit(10).all()
    
    # Statistics
    stats = {
        "doctor_info": {
            "name": doctor.full_name if doctor else current_user.full_name,
            "specialization": doctor.specialization if doctor else None,
            "registration": doctor.registration_number if doctor else None,
            "verification_status": doctor.verification_status if doctor else "unverified"
        },
        "blog_stats": {
            "total": my_blogs,
            "pending": pending_blogs,
            "approved": approved_blogs
        },
        "case_stats": {
            "total_consultations": len(recent_cases),
            "recent_cases": [
                {
                    "id": case.id,
                    "predicted_poison": case.predicted_poison,
                    "severity": case.severity_assessment,
                    "date": case.created_at.isoformat()
                } for case in recent_cases[:5]
            ]
        }
    }
    
    return stats


@router.get("/hospital")
async def get_hospital_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Hospital Admin Dashboard - Shows facility stats, antidotes, cases
    """
    if current_user.role != "hospital_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital admin privileges required"
        )
    
    # Get hospital info
    hospital = db.query(Hospital).filter(Hospital.admin_id == current_user.id).first()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hospital associated with this account"
        )
    
    # Get cases handled by hospital (from AI logs)
    total_cases = db.query(AnalysisLog).filter(
        AnalysisLog.hospital_referred == True
    ).count()
    
    recent_cases = db.query(AnalysisLog).filter(
        AnalysisLog.hospital_referred == True
    ).order_by(AnalysisLog.created_at.desc()).limit(10).all()
    
    # Get emergency cases (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    emergency_cases_week = db.query(AnalysisLog).filter(
        and_(
            AnalysisLog.hospital_referred == True,
            AnalysisLog.created_at >= week_ago,
            AnalysisLog.severity_assessment.in_(["severe", "critical"])
        )
    ).count()
    
    # Statistics
    stats = {
        "hospital_info": {
            "name": hospital.name,
            "type": hospital.hospital_type,
            "city": hospital.city,
            "emergency_phone": hospital.emergency_phone,
            "is_24_hours": hospital.is_24_hours
        },
        "facility_info": {
            "facilities": hospital.facilities if hasattr(hospital, 'facilities') else [],
            "antidotes_available": hospital.antidotes_available if hasattr(hospital, 'antidotes_available') else [],
            "toxicology_tests": hospital.toxicology_tests if hasattr(hospital, 'toxicology_tests') else []
        },
        "case_stats": {
            "total_cases": total_cases,
            "emergency_cases_this_week": emergency_cases_week,
            "recent_cases": [
                {
                    "id": case.id,
                    "predicted_poison": case.predicted_poison,
                    "severity": case.severity_assessment,
                    "antidote": case.antidote_suggested,
                    "date": case.created_at.isoformat()
                } for case in recent_cases[:5]
            ]
        }
    }
    
    return stats


@router.get("/blog-reviewer")
async def get_reviewer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Blog Reviewer Dashboard - Shows pending blogs and review statistics
    """
    if current_user.role not in ["blog_reviewer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Blog reviewer privileges required"
        )
    
    # Get pending blogs
    pending_count = db.query(BlogSubmission).filter(
        BlogSubmission.status == "pending"
    ).count()
    
    # Get reviews by this reviewer
    my_reviews = db.query(BlogSubmission).filter(
        BlogSubmission.reviewed_by == current_user.id
    ).count()
    
    # Get recent pending submissions
    recent_pending = db.query(BlogSubmission).filter(
        BlogSubmission.status == "pending"
    ).order_by(BlogSubmission.created_at.desc()).limit(10).all()
    
    # Statistics
    stats = {
        "reviewer_info": {
            "name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role
        },
        "review_stats": {
            "pending_submissions": pending_count,
            "total_reviewed": my_reviews,
            "recent_pending": [
                {
                    "id": blog.id,
                    "title": blog.title,
                    "author": blog.author_name,
                    "category": blog.category,
                    "submitted": blog.created_at.isoformat()
                } for blog in recent_pending
            ]
        }
    }
    
    return stats
