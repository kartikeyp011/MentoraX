from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class CareerPathRequest(BaseModel):
    """Request for career path suggestions"""
    user_profile: Optional[dict] = None  # Auto-filled from JWT
    skills: Optional[List[str]] = None
    degree: Optional[str] = None
    career_interests: Optional[List[str]] = None

class CareerOption(BaseModel):
    """Individual career path option"""
    title: str
    description: str
    required_skills: List[str]
    missing_skills: List[str]
    salary_range: Optional[str] = None
    growth_potential: str  # high, medium, low
    match_percentage: int = Field(..., ge=0, le=100)

class CareerPathResponse(BaseModel):
    """AI-generated career paths"""
    career_options: List[CareerOption]
    recommended_path: str
    next_steps: List[str]
    learning_recommendations: List[str]

class DegreeMapRequest(BaseModel):
    """Map degree to career options"""
    degree: str = Field(..., min_length=1)
    specialization: Optional[str] = None

class DegreeMapResponse(BaseModel):
    """Degree mapping result"""
    degree: str
    career_paths: List[str]
    top_skills: List[str]
    industry_trends: List[str]
