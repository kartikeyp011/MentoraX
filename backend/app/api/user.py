from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserProfileResponse,
    UserUpdate,
    UserStatsResponse,
    UserSkillResponse,
    SkillBase
)
from app.schemas.resume import ResumeUploadResponse
from app.services.user_service import user_service
from app.services.s3_service import s3_service

router = APIRouter(prefix="/user", tags=["User Management"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile with skills
    """
    # Get user skills
    skills = user_service.get_user_skills(current_user.user_id, db)
    
    return UserProfileResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        email=current_user.email,
        degree=current_user.degree,
        career_goal=current_user.career_goal,
        skills=[UserSkillResponse(**skill) for skill in skills],
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    Can update: name, degree, career_goal, skills
    """
    updated_user = user_service.update_user_profile(
        current_user.user_id,
        update_data,
        db
    )
    
    # Get updated skills
    skills = user_service.get_user_skills(updated_user.user_id, db)
    
    return UserProfileResponse(
        user_id=updated_user.user_id,
        name=updated_user.name,
        email=updated_user.email,
        degree=updated_user.degree,
        career_goal=updated_user.career_goal,
        skills=[UserSkillResponse(**skill) for skill in skills],
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    Returns: total skills, saved opportunities, profile completion
    """
    return user_service.get_user_stats(current_user.user_id, db)

@router.post("/skills/add")
async def add_skill(
    skill_data: SkillBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a single skill to user profile
    """
    user_skill = user_service.add_user_skill(
        current_user.user_id,
        skill_data.skill_name,
        skill_data.proficiency or 1,
        db
    )
    
    return {
        "success": True,
        "message": f"Skill '{skill_data.skill_name}' added successfully",
        "skill_id": user_skill.skill_id,
        "proficiency": user_skill.proficiency
    }

@router.delete("/skills/{skill_id}")
async def remove_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a skill from user profile
    """
    user_service.remove_user_skill(current_user.user_id, skill_id, db)
    
    return {
        "success": True,
        "message": "Skill removed successfully"
    }

@router.get("/skills", response_model=List[UserSkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all skills for current user
    """
    skills = user_service.get_user_skills(current_user.user_id, db)
    return [UserSkillResponse(**skill) for skill in skills]

@router.post("/upload_resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload user resume (PDF only, max 1MB)
    Stores in AWS S3 and creates database record
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size (1MB = 1048576 bytes)
    if len(content) > 1048576:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 1MB"
        )
    
    try:
        # Upload to S3 (we'll implement this service next)
        resume = await s3_service.upload_resume(
            user_id=current_user.user_id,
            file_content=content,
            file_name=file.filename,
            db=db
        )
        
        return ResumeUploadResponse(
            resume_id=resume.resume_id,
            file_url=resume.file_url,
            file_name=resume.file_name,
            uploaded_at=resume.uploaded_at,
            success=True,
            message="Resume uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )

@router.get("/resumes")
async def get_user_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resumes uploaded by user
    """
    resumes = db.query(User).filter(
        User.user_id == current_user.user_id
    ).first().resumes
    
    return {
        "resumes": [
            {
                "resume_id": r.resume_id,
                "file_name": r.file_name,
                "file_url": r.file_url,
                "uploaded_at": r.uploaded_at
            }
            for r in resumes
        ]
    }

@router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a resume
    """
    try:
        await s3_service.delete_resume(
            resume_id=resume_id,
            user_id=current_user.user_id,
            db=db
        )
        
        return {
            "success": True,
            "message": "Resume deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )
