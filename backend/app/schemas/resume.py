from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ResumeUploadResponse(BaseModel):
    """Resume upload confirmation"""
    resume_id: int
    file_url: str
    file_name: str
    uploaded_at: datetime
    success: bool
    message: str

class ResumeResponse(BaseModel):
    """Resume details"""
    resume_id: int
    file_url: str
    file_name: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class ResumeAnalysisRequest(BaseModel):
    """Analyze resume content"""
    resume_id: Optional[int] = None
    resume_text: Optional[str] = None

class ResumeAnalysisResponse(BaseModel):
    """Resume analysis results"""
    extracted_skills: List[str]
    experience_level: str
    suggested_roles: List[str]
    improvement_tips: List[str]
