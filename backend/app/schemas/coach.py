from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CoachChatRequest(BaseModel):
    """Chat message to AI coach"""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[dict] = None  # Previous conversation context

class CoachChatResponse(BaseModel):
    """AI coach response"""
    response: str
    suggested_resources: Optional[List[dict]] = None
    action_items: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SkillPlanRequest(BaseModel):
    """Request personalized skill plan"""
    target_role: Optional[str] = None
    timeline: Optional[str] = "3 months"  # 1 month, 3 months, 6 months

class SkillPlanStep(BaseModel):
    """Individual learning step"""
    step_number: int
    skill_name: str
    description: str
    estimated_time: str
    resources: List[dict]
    priority: str  # high, medium, low

class SkillPlanResponse(BaseModel):
    """Personalized learning plan"""
    plan_title: str
    total_duration: str
    steps: List[SkillPlanStep]
    milestones: List[str]
