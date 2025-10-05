from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class CareerPath(Base):
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    role_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(JSON, nullable=True)
    salary_range = Column(String(100), nullable=True)
    growth_potential = Column(String(50), nullable=True)
    
    learning_roadmap = Column(JSON, nullable=True)
    estimated_time = Column(String(100), nullable=True)
    
    is_saved = Column(Integer, default=0)
    progress = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="career_paths")


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    target_role = Column(String(255), nullable=False)
    current_skills = Column(JSON, nullable=True)
    required_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True)
    
    recommendations = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
