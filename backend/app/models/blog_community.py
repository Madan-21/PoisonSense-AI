# Blog Community Features - Comments, Likes, and Reputation
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class ReputationLevel(str, enum.Enum):
    NEWCOMER = "newcomer"  # 0-50
    CONTRIBUTOR = "contributor"  # 51-500
    TRUSTED = "trusted"  # 501-2000
    EXPERT = "expert"  # 2001+


class BlogComment(Base):
    """Blog comment model for community engagement"""
    __tablename__ = "blog_comments"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blog_submissions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("blog_comments.id", ondelete="CASCADE"), nullable=True)  # For nested comments
    
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    blog = relationship("BlogSubmission", backref="comments")
    author = relationship("User", foreign_keys=[user_id], backref="blog_comments")
    parent = relationship("BlogComment", remote_side=[id], backref="replies")


class BlogLike(Base):
    """Blog like/reaction model"""
    __tablename__ = "blog_likes"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blog_submissions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog = relationship("BlogSubmission", backref="likes")
    user = relationship("User", backref="blog_likes")


class BlogBookmark(Base):
    """Blog bookmark/save model"""
    __tablename__ = "blog_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blog_submissions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    blog = relationship("BlogSubmission", backref="bookmarks")
    user = relationship("User", backref="blog_bookmarks")


class UserReputation(Base):
    """User reputation and badges for community engagement"""
    __tablename__ = "user_reputation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    points = Column(Integer, default=0)
    level = Column(Enum(ReputationLevel), default=ReputationLevel.NEWCOMER)
    badges = Column(Text)  # JSON array of badges
    
    # Stats
    articles_published = Column(Integer, default=0)
    comments_posted = Column(Integer, default=0)
    likes_received = Column(Integer, default=0)
    helpful_answers = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="reputation")


class CommentLike(Base):
    """Likes on comments"""
    __tablename__ = "comment_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("blog_comments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    comment = relationship("BlogComment")
    user = relationship("User")
