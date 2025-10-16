from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class ResourceBase(BaseModel):
    """Base resource fields"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: str = Field(..., max_length=255)
    resource_type: Optional[str] = Field(None, max_length=50)  # course, video, article

class ResourceCreate(ResourceBase):
    """Create resource"""
    related_skills: Optional[List[str]] = []

class ResourceResponse(ResourceBase):
    """Resource response"""
    resource_id: int
    related_skills: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResourceSearchRequest(BaseModel):
    """Search resources"""
    query: str = Field(..., min_length=1)
    skill_filter: Optional[List[str]] = None
    resource_type: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)

class ResourceSearchResponse(BaseModel):
    """Search results"""
    resources: List[ResourceResponse]
    total: int
    query: str
