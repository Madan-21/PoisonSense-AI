# Blog Schemas
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class BlogSubmissionCreate(BaseModel):
    """Schema for creating a blog submission"""
    title: str = Field(..., min_length=10, max_length=255)
    category: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=50, max_length=500)
    content: str = Field(..., min_length=100)
    featured_image: Optional[str] = None
    additional_files: Optional[List[str]] = None
    is_original: bool = True
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = ['Prevention', 'First Aid', 'Case Studies', 'Research', 'Safety Tips', 'Antidotes']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v


class BlogSubmissionUpdate(BaseModel):
    """Schema for updating a blog submission"""
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    category: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=50, max_length=500)
    content: Optional[str] = Field(None, min_length=100)
    featured_image: Optional[str] = None
    additional_files: Optional[List[str]] = None


class BlogSubmissionResponse(BaseModel):
    """Schema for blog submission response"""
    id: int
    title: str
    category: str
    description: str
    content: str
    featured_image: Optional[str]
    additional_files: Optional[str]
    
    author_id: int
    author_name: str
    author_email: str
    is_original: bool
    
    status: str
    reviewed_by: Optional[int]
    review_comment: Optional[str]
    reviewed_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    read_time: Optional[str]
    view_count: int
    
    model_config = {
        "from_attributes": True
    }


class BlogSubmissionList(BaseModel):
    """Schema for blog submission list item"""
    id: int
    title: str
    category: str
    description: str
    author_name: str
    status: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class BlogReviewAction(BaseModel):
    """Schema for reviewing a blog submission"""
    comment: Optional[str] = None


class PublishedArticle(BaseModel):
    """Schema for published blog article (public view)"""
    id: int
    title: str
    category: str
    description: str
    content: str
    featured_image: Optional[str]
    author_name: str
    published_at: datetime
    read_time: Optional[str]
    view_count: int
    
    model_config = {
        "from_attributes": True
    }
