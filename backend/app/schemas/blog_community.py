# Blog Community Schemas
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BlogCommentCreate(BaseModel):
    """Schema for creating a blog comment"""
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[int] = None  # For nested replies


class BlogCommentResponse(BaseModel):
    """Schema for blog comment response"""
    id: int
    blog_id: int
    user_id: int
    parent_id: Optional[int]
    content: str
    is_edited: bool
    author_name: str
    author_email: str
    created_at: datetime
    updated_at: datetime
    replies_count: int = 0
    
    model_config = {
        "from_attributes": True
    }


class BlogLikeResponse(BaseModel):
    """Schema for blog like response"""
    blog_id: int
    total_likes: int
    user_liked: bool


class BlogBookmarkResponse(BaseModel):
    """Schema for blog bookmark response"""
    blog_id: int
    is_bookmarked: bool


class BlogCommunityStats(BaseModel):
    """Schema for blog community statistics"""
    blog_id: int
    likes_count: int
    comments_count: int
    bookmarks_count: int
    view_count: int
