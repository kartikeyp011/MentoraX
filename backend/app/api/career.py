from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.career import (
    CareerPathRequest,
    CareerPathResponse,
    DegreeMapRequest,
    DegreeMapResponse
)
from app.schemas.skill import (
    SkillAnalysisRequest,
    SkillAnalysisResponse
)
from app.services.ai_service import ai_service
from app.services.user_service import user_service

router = APIRouter(prefix="/career", tags=["Career Guidance"])

@router.post("/path", response_model=CareerPathResponse)
async def get_career_path(
    request: CareerPathRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered career path recommendations
    Based on user profile, skills, degree, and interests
    """
    # Get user skills if not provided
    if request.skills is None:
        user_skills = user_service.get_user_skills(current_user.user_id, db)
        skills = [skill['skill_name'] for skill in user_skills]
    else:
        skills = request.skills
    
    # Use user's degree if not provided
    degree = request.degree or current_user.degree
    
    # Build user profile
    user_profile = {
        'name': current_user.name,
        'career_goal': current_user.career_goal
    }
    
    # Generate career paths
    career_data = await ai_service.generate_career_paths(
        user_profile=user_profile,
        skills=skills,
        degree=degree,
        career_interests=request.career_interests
    )
    
    return CareerPathResponse(**career_data)

@router.post("/skills/analyze", response_model=SkillAnalysisResponse)
async def analyze_skills(
    request: SkillAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze skill gaps for a target role
    Can use resume text or current skills list
    """
    # Get current skills if not provided
    if not request.current_skills:
        user_skills = user_service.get_user_skills(current_user.user_id, db)
        current_skills = [skill['skill_name'] for skill in user_skills]
    else:
        current_skills = request.current_skills
    
    # Use career goal if target role not provided
    target_role = request.target_role or current_user.career_goal or "General Career Development"
    
    # Analyze skill gaps
    skill_gap_data = await ai_service.analyze_skill_gaps(
        current_skills=current_skills,
        target_role=target_role,
        resume_text=request.resume_text
    )
    
    return SkillAnalysisResponse(**skill_gap_data)

@router.post("/degree/map", response_model=DegreeMapResponse)
async def map_degree(
    request: DegreeMapRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Map a degree to potential career paths
    Shows career options, required skills, and industry trends
    """
    degree_data = await ai_service.map_degree_to_careers(
        degree=request.degree,
        specialization=request.specialization
    )
    
    return DegreeMapResponse(**degree_data)
