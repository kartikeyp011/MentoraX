from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from datetime import datetime, date

class OpportunityBase(BaseModel):
    """Base opportunity fields"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    link: str = Field(..., max_length=255)
    source: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    deadline: Optional[date] = None

class OpportunityCreate(OpportunityBase):
    """Create opportunity"""
    required_skills: Optional[List[str]] = []

class OpportunityResponse(OpportunityBase):
    """Opportunity response"""
    opportunity_id: int
    required_skills: List[str] = []
    created_at: datetime
    updated_at: datetime
    is_saved: bool = False  # For authenticated user
    
    class Config:
        from_attributes = True

class OpportunityFilterRequest(BaseModel):
    """Filter opportunities"""
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    source: Optional[str] = None
    opportunity_type: Optional[str] = None  # internship, job, scholarship
    deadline_before: Optional[date] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class OpportunitiesListResponse(BaseModel):
    """Paginated opportunities list"""
    opportunities: List[OpportunityResponse]
    total: int
    limit: int
    offset: int

class SaveOpportunityRequest(BaseModel):
    """Save/bookmark opportunity"""
    opportunity_id: int

class SaveOpportunityResponse(BaseModel):
    """Save opportunity response"""
    success: bool
    message: str
    opportunity_id: int
