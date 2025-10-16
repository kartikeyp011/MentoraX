from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SkillBase(BaseModel):
    """Base skill schema"""
    skill_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class SkillCreate(SkillBase):
    """Create new skill"""
    pass

class SkillResponse(SkillBase):
    """Skill response with ID"""
    skill_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SkillAnalysisRequest(BaseModel):
    """Request for skill gap analysis"""
    resume_text: Optional[str] = None
    current_skills: List[str] = []
    target_role: Optional[str] = None

class SkillGap(BaseModel):
    """Individual skill gap"""
    skill_name: str
    importance: str  # high, medium, low
    reason: str

class SkillAnalysisResponse(BaseModel):
    """AI-powered skill gap analysis"""
    current_skills: List[str]
    missing_skills: List[SkillGap]
    recommended_skills: List[SkillGap]
    learning_path: List[str]
