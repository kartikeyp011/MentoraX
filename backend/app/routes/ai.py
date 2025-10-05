from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.gemini_service import gemini_service
from app.models.user import User
from app.models.career import CareerPath, SkillGapAnalysis
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/ai", tags=["AI Services"])

# ========== Request Models ==========

class CareerPathRequest(BaseModel):
    user_id: int
    degree: str
    skills: List[str]
    interests: List[str]
    career_goals: Optional[str] = None

class SkillGapRequest(BaseModel):
    user_id: int
    target_role: str
    current_skills: List[str]
    experience_level: str = "entry"

class DegreeCareersRequest(BaseModel):
    degree: str
    specialization: Optional[str] = None

class ResumeAnalysisRequest(BaseModel):
    resume_text: str

class ResumeGenerationRequest(BaseModel):
    user_id: int
    target_role: Optional[str] = None

class InterviewQuestionsRequest(BaseModel):
    role: str
    difficulty: str = "medium"
    count: int = 10

class InterviewAnswerRequest(BaseModel):
    question: str
    user_answer: str
    ideal_answer_points: List[str]

class LearningPathRequest(BaseModel):
    skill: str
    current_level: str = "beginner"
    time_commitment: str = "flexible"

class SentimentRequest(BaseModel):
    text: str

class JobTaskRequest(BaseModel):
    role: str
    difficulty: str = "medium"

class TaskSubmissionRequest(BaseModel):
    task_description: str
    submission: str
    evaluation_criteria: List[str]

# ========== Endpoints ==========

@router.post("/career-paths")
async def generate_career_paths(
    request: CareerPathRequest,
    db: Session = Depends(get_db)
):
    """Generate AI-powered career path recommendations"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate career paths
    career_paths = gemini_service.generate_career_paths(
        degree=request.degree,
        skills=request.skills,
        interests=request.interests,
        career_goals=request.career_goals
    )
    
    if not career_paths:
        raise HTTPException(status_code=500, detail="Failed to generate career paths")
    
    # Save to database
    saved_paths = []
    for path in career_paths:
        db_path = CareerPath(
            user_id=request.user_id,
            role_title=path.get('role_title'),
            description=path.get('description'),
            required_skills=path.get('required_skills'),
            salary_range=path.get('salary_range'),
            growth_potential=path.get('growth_potential'),
            learning_roadmap=path.get('learning_roadmap'),
            estimated_time=path.get('estimated_time')
        )
        db.add(db_path)
        saved_paths.append(path)
    
    db.commit()
    
    return {
        "message": "Career paths generated successfully",
        "career_paths": saved_paths
    }

@router.post("/skill-gap-analysis")
async def analyze_skill_gap(
    request: SkillGapRequest,
    db: Session = Depends(get_db)
):
    """Analyze skill gaps for target role"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Analyze skill gap
    analysis = gemini_service.analyze_skill_gap(
        current_skills=request.current_skills,
        target_role=request.target_role,
        experience_level=request.experience_level
    )
    
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze skill gap")
    
    # Save to database
    db_analysis = SkillGapAnalysis(
        user_id=request.user_id,
        target_role=request.target_role,
        current_skills=request.current_skills,
        required_skills=analysis.get('required_skills'),
        missing_skills=analysis.get('missing_skills'),
        skill_gaps=analysis.get('skill_gaps'),
        recommendations=analysis.get('recommendations')
    )
    db.add(db_analysis)
    db.commit()
    
    return {
        "message": "Skill gap analysis completed",
        "analysis": analysis
    }

@router.post("/degree-careers")
async def get_degree_careers(request: DegreeCareersRequest):
    """Get career options for a degree"""
    
    careers = gemini_service.map_degree_to_careers(
        degree=request.degree,
        specialization=request.specialization
    )
    
    if not careers:
        raise HTTPException(status_code=500, detail="Failed to generate career options")
    
    return {
        "message": "Career options generated successfully",
        "careers": careers
    }

@router.post("/resume/analyze")
async def analyze_resume(request: ResumeAnalysisRequest):
    """Analyze resume and provide feedback"""
    
    analysis = gemini_service.analyze_resume(request.resume_text)
    
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze resume")
    
    return {
        "message": "Resume analyzed successfully",
        "analysis": analysis
    }

@router.post("/resume/generate")
async def generate_resume(
    request: ResumeGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate resume content"""
    
    # Get user profile
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare user profile
    user_profile = {
        "name": user.name,
        "email": user.email,
        "degree": user.degree,
        "specialization": user.specialization,
        "college": user.college,
        "graduation_year": user.graduation_year,
        "skills": user.skills,
        "interests": user.interests,
        "career_goals": user.career_goals
    }
    
    # Generate resume content
    content = gemini_service.generate_resume_content(
        user_profile=user_profile,
        target_role=request.target_role
    )
    
    if not content:
        raise HTTPException(status_code=500, detail="Failed to generate resume content")
    
    return {
        "message": "Resume content generated successfully",
        "content": content
    }

@router.post("/interview/questions")
async def generate_interview_questions(request: InterviewQuestionsRequest):
    """Generate interview questions"""
    
    questions = gemini_service.generate_interview_questions(
        role=request.role,
        difficulty=request.difficulty,
        count=request.count
    )
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions")
    
    return {
        "message": "Interview questions generated successfully",
        "questions": questions
    }

@router.post("/interview/evaluate")
async def evaluate_answer(request: InterviewAnswerRequest):
    """Evaluate interview answer"""
    
    evaluation = gemini_service.evaluate_interview_answer(
        question=request.question,
        user_answer=request.user_answer,
        ideal_answer_points=request.ideal_answer_points
    )
    
    if not evaluation:
        raise HTTPException(status_code=500, detail="Failed to evaluate answer")
    
    return {
        "message": "Answer evaluated successfully",
        "evaluation": evaluation
    }

@router.post("/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """Generate learning path for a skill"""
    
    path = gemini_service.generate_learning_path(
        skill=request.skill,
        current_level=request.current_level,
        time_commitment=request.time_commitment
    )
    
    if not path:
        raise HTTPException(status_code=500, detail="Failed to generate learning path")
    
    return {
        "message": "Learning path generated successfully",
        "learning_path": path
    }

@router.post("/sentiment/analyze")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of text"""
    
    analysis = gemini_service.analyze_sentiment(request.text)
    
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze sentiment")
    
    return {
        "message": "Sentiment analyzed successfully",
        "analysis": analysis
    }

@router.post("/job-simulator/task")
async def generate_job_task(request: JobTaskRequest):
    """Generate job simulation task"""
    
    task = gemini_service.generate_job_task(
        role=request.role,
        difficulty=request.difficulty
    )
    
    if not task:
        raise HTTPException(status_code=500, detail="Failed to generate task")
    
    return {
        "message": "Job task generated successfully",
        "task": task
    }

@router.post("/job-simulator/evaluate")
async def evaluate_task_submission(request: TaskSubmissionRequest):
    """Evaluate job task submission"""
    
    evaluation = gemini_service.evaluate_job_task_submission(
        task_description=request.task_description,
        submission=request.submission,
        evaluation_criteria=request.evaluation_criteria
    )
    
    if not evaluation:
        raise HTTPException(status_code=500, detail="Failed to evaluate submission")
    
    return {
        "message": "Submission evaluated successfully",
        "evaluation": evaluation
    }
