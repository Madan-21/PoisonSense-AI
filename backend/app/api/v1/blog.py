# Blog Submission API Endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.db.session import get_db
from app.models.user import User
from app.models.blog_submission import BlogSubmission
from app.schemas.blog import (
    BlogSubmissionCreate,
    BlogSubmissionUpdate,
    BlogSubmissionResponse,
    BlogSubmissionList,
    BlogReviewAction,
    PublishedArticle
)
from app.core.security import get_current_user, get_current_user_required

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.post("/submissions", response_model=BlogSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_submission(
    submission: BlogSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Create a new blog submission.
    
    - **title**: Article title (10-255 characters)
    - **category**: Category (Prevention, First Aid, Case Studies, Research, Safety Tips, Antidotes)
    - **description**: Short description (50-500 characters)
    - **content**: Full article content (minimum 100 characters)
    - **featured_image**: Optional image URL
    - **additional_files**: Optional list of file names
    - **is_original**: Whether the content is original (default: True)
    """
    # Calculate estimated read time
    words = len(submission.content.split())
    read_time = f"{max(1, words // 200)} min read"
    
    # Convert additional_files list to JSON string
    additional_files_str = None
    if submission.additional_files:
        additional_files_str = json.dumps(submission.additional_files)
    
    db_submission = BlogSubmission(
        title=submission.title,
        category=submission.category,
        description=submission.description,
        content=submission.content,
        featured_image=submission.featured_image,
        additional_files=additional_files_str,
        author_id=current_user.id,
        author_name=current_user.full_name or current_user.email,
        author_email=current_user.email,
        is_original=submission.is_original,
        read_time=read_time,
        status="pending"
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    return db_submission


@router.get("/submissions", response_model=List[BlogSubmissionList])
async def get_all_submissions(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Get all blog submissions (admin only).
    
    - **status_filter**: Optional filter by status (pending, approved, rejected)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all submissions"
        )
    
    query = db.query(BlogSubmission)
    
    if status_filter:
        query = query.filter(BlogSubmission.status == status_filter)
    
    submissions = query.order_by(BlogSubmission.created_at.desc()).all()
    return submissions


@router.get("/submissions/my", response_model=List[BlogSubmissionResponse])
async def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get current user's blog submissions"""
    submissions = db.query(BlogSubmission).filter(
        BlogSubmission.author_id == current_user.id
    ).order_by(BlogSubmission.created_at.desc()).all()
    
    return submissions


@router.get("/submissions/{submission_id}", response_model=BlogSubmissionResponse)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get a specific blog submission"""
    submission = db.query(BlogSubmission).filter(
        BlogSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog submission not found"
        )
    
    # Only admin or author can view
    if current_user.role != "admin" and submission.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this submission"
        )
    
    return submission


@router.post("/submissions/{submission_id}/approve", response_model=BlogSubmissionResponse)
async def approve_submission(
    submission_id: int,
    review: BlogReviewAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Approve a blog submission (admin only).
    
    - **comment**: Optional review comment
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve submissions"
        )
    
    submission = db.query(BlogSubmission).filter(
        BlogSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog submission not found"
        )
    
    if submission.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already approved"
        )
    
    submission.status = "approved"
    submission.reviewed_by = current_user.id
    submission.review_comment = review.comment
    submission.reviewed_at = datetime.utcnow()
    submission.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    return submission


@router.post("/submissions/{submission_id}/reject", response_model=BlogSubmissionResponse)
async def reject_submission(
    submission_id: int,
    review: BlogReviewAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Reject a blog submission (admin only).
    
    - **comment**: Optional review comment explaining rejection
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reject submissions"
        )
    
    submission = db.query(BlogSubmission).filter(
        BlogSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog submission not found"
        )
    
    if submission.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already rejected"
        )
    
    submission.status = "rejected"
    submission.reviewed_by = current_user.id
    submission.review_comment = review.comment
    submission.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    return submission


@router.delete("/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Delete a blog submission (author or admin only)"""
    submission = db.query(BlogSubmission).filter(
        BlogSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog submission not found"
        )
    
    # Only admin or author can delete
    if current_user.role != "admin" and submission.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this submission"
        )
    
    db.delete(submission)
    db.commit()
    
    return None


# Public endpoints for viewing published articles
@router.get("/articles", response_model=List[PublishedArticle])
async def get_published_articles(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all published blog articles (public endpoint).
    
    - **category**: Optional filter by category
    """
    query = db.query(BlogSubmission).filter(BlogSubmission.status == "approved")
    
    if category:
        query = query.filter(BlogSubmission.category == category)
    
    articles = query.order_by(BlogSubmission.published_at.desc()).all()
    return articles


@router.get("/articles/{article_id}", response_model=PublishedArticle)
async def get_published_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific published article (public endpoint)"""
    article = db.query(BlogSubmission).filter(
        BlogSubmission.id == article_id,
        BlogSubmission.status == "approved"
    ).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Increment view count
    article.view_count += 1
    db.commit()
    
    return article
