from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    auth0_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    profile_picture = Column(String(500), nullable=True)
    
    degree = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    college = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    
    career_goals = Column(Text, nullable=True)
    interests = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    
    profile_completion = Column(Integer, default=0)
    
    resume_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    career_paths = relationship("CareerPath", back_populates="user", cascade="all, delete-orphan")
    saved_opportunities = relationship("SavedOpportunity", back_populates="user", cascade="all, delete-orphan")
    mental_health_logs = relationship("MentalHealthLog", back_populates="user", cascade="all, delete-orphan")
    mentorship_requests = relationship("MentorshipConnection", foreign_keys="[MentorshipConnection.student_id]", back_populates="student")
