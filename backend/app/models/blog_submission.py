# Blog Submission Model
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class BlogSubmission(Base):
    """Blog article submission model"""
    __tablename__ = "blog_submissions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    featured_image = Column(String(500), nullable=True)
    additional_files = Column(Text, nullable=True)  # JSON string of file names
    
    # Submission metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(200), nullable=False)
    author_email = Column(String(200), nullable=False)
    is_original = Column(Boolean, default=True)
    
    # Review status
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Published article fields (only filled after approval)
    published_at = Column(DateTime, nullable=True)
    read_time = Column(String(20), nullable=True)
    view_count = Column(Integer, default=0)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id], backref="blog_submissions")
    reviewer = relationship("User", foreign_keys=[reviewed_by], backref="reviewed_submissions")
