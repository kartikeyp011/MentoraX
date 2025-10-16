from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

class SkillBase(BaseModel):
    """Base skill schema"""
    skill_name: str
    proficiency: Optional[int] = Field(1, ge=1, le=5)

class UserSkillResponse(BaseModel):
    """User skill with details"""
    skill_id: int
    skill_name: str
    proficiency: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Base user fields"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    degree: Optional[str] = Field(None, max_length=50)
    career_goal: Optional[str] = Field(None, max_length=255)

class UserCreate(UserBase):
    """User creation schema"""
    auth0_id: str = Field(..., description="Auth0 user identifier")

class UserUpdate(BaseModel):
    """User update schema - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    degree: Optional[str] = Field(None, max_length=50)
    career_goal: Optional[str] = Field(None, max_length=255)
    skills: Optional[List[SkillBase]] = None

class UserProfileResponse(BaseModel):
    """Complete user profile response"""
    user_id: int
    name: str
    email: str
    degree: Optional[str]
    career_goal: Optional[str]
    skills: List[UserSkillResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    """Dashboard statistics"""
    total_skills: int
    saved_opportunities: int
    completed_resources: int
    profile_completion: int  # Percentage
