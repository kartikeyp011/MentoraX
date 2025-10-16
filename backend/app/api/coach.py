from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
    SkillPlanRequest,
    SkillPlanResponse
)
from app.services.ai_service import ai_service
from app.services.user_service import user_service
router = APIRouter(prefix="/coach", tags=["AI Coach"])

@router.post("/chat", response_model=CoachChatResponse)
async def chat_with_coach(
    request: CoachChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI career coach
    Provides personalized advice and guidance
    """
    # Get user skills for context
    user_skills = user_service.get_user_skills(current_user.user_id, db)
    skills = [skill['skill_name'] for skill in user_skills]
    
    # Build user context
    user_context = {
        'skills': skills,
        'degree': current_user.degree,
        'career_goal': current_user.career_goal,
        'name': current_user.name
    }
    
    # Add previous context if provided
    if request.context:
        user_context.update(request.context)
    
    # Generate response
    coach_response = await ai_service.generate_coach_response(
        user_message=request.message,
        user_context=user_context
    )
    
    return CoachChatResponse(**coach_response)

@router.get("/plan", response_model=SkillPlanResponse)
async def get_skill_plan(
    target_role: str = None,
    timeline: str = "3 months",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized skill development plan
    Timeline options: "1 month", "3 months", "6 months"
    """
    # Get user skills
    user_skills = user_service.get_user_skills(current_user.user_id, db)
    skills = [skill['skill_name'] for skill in user_skills]
    
    # Build user profile
    user_profile = {
        'name': current_user.name,
        'degree': current_user.degree,
        'career_goal': current_user.career_goal
    }
    
    # Generate skill plan
    plan_data = await ai_service.generate_skill_plan(
        user_profile=user_profile,
        current_skills=skills,
        target_role=target_role,
        timeline=timeline
    )
    
    return SkillPlanResponse(**plan_data)

@router.post("/plan", response_model=SkillPlanResponse)
async def create_custom_skill_plan(
    request: SkillPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create custom skill development plan with specific parameters
    """
    # Get user skills
    user_skills = user_service.get_user_skills(current_user.user_id, db)
    skills = [skill['skill_name'] for skill in user_skills]
    
    # Build user profile
    user_profile = {
        'name': current_user.name,
        'degree': current_user.degree,
        'career_goal': current_user.career_goal
    }
    
    # Generate skill plan
    plan_data = await ai_service.generate_skill_plan(
        user_profile=user_profile,
        current_skills=skills,
        target_role=request.target_role,
        timeline=request.timeline
    )
    
    return SkillPlanResponse(**plan_data)
