from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    degree: Optional[str] = None
    career_goal: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    user_id: int
    name: str
    email: str
    degree: Optional[str]
    career_goal: Optional[str]
    resume_url: Optional[str]
    skills: List[dict] = []  # [{"skill_id": 1, "skill_name": "Python", "proficiency": 4}]

class CareerPathRequest(BaseModel):
    user_id: int

class CareerPath(BaseModel):
    title: str
    fit_reason: str
    missing_skills: List[str]
    roadmap: List[str]

class OpportunityFilter(BaseModel):
    skill_ids: Optional[List[int]] = None
    location: Optional[str] = None
    deadline_after: Optional[date] = None

class ResourceSearch(BaseModel):
    query: str
    skill_filter: Optional[List[int]] = None

class UpdateProfile(BaseModel):
    degree: Optional[str] = None
    career_goal: Optional[str] = None
    skills: Optional[List[dict]] = None  # [{"skill_id": 1, "proficiency": 4}]