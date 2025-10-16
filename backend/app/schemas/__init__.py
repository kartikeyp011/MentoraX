from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.auth import *
from app.schemas.user import *
from app.schemas.skill import *
from app.schemas.opportunity import *
from app.schemas.resource import *
from app.schemas.career import *
from app.schemas.coach import *
from app.schemas.resume import *

__all__ = [
    # Auth
    "Auth0Token",
    "TokenResponse",
    "LoginRequest",
    "LoginResponse",
    "LogoutResponse",
    
    # User
    "UserCreate",
    "UserUpdate",
    "UserProfileResponse",
    "UserStatsResponse",
    "UserSkillResponse",
    
    # Skill
    "SkillCreate",
    "SkillResponse",
    "SkillAnalysisRequest",
    "SkillAnalysisResponse",
    
    # Opportunity
    "OpportunityCreate",
    "OpportunityResponse",
    "OpportunityFilterRequest",
    "OpportunitiesListResponse",
    "SaveOpportunityRequest",
    
    # Resource
    "ResourceCreate",
    "ResourceResponse",
    "ResourceSearchRequest",
    "ResourceSearchResponse",
    
    # Career
    "CareerPathRequest",
    "CareerPathResponse",
    "DegreeMapRequest",
    "DegreeMapResponse",
    
    # Coach
    "CoachChatRequest",
    "CoachChatResponse",
    "SkillPlanRequest",
    "SkillPlanResponse",
    
    # Resume
    "ResumeUploadResponse",
    "ResumeAnalysisRequest",
    "ResumeAnalysisResponse",
]

class ResponseBase(BaseModel):
    """Base response schema"""
    success: bool
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
