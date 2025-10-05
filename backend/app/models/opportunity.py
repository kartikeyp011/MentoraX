from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base
import enum

class OpportunityType(enum.Enum):
    JOB = "job"
    INTERNSHIP = "internship"
    HACKATHON = "hackathon"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True, index=True)
    type = Column(Enum(OpportunityType), nullable=False, index=True)
    
    description = Column(Text, nullable=True)
    requirements = Column(JSON, nullable=True)
    skills_required = Column(JSON, nullable=True)
    
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=False)
    salary_range = Column(String(100), nullable=True)
    stipend = Column(String(100), nullable=True)
    
    application_url = Column(String(500), nullable=True)
    deadline = Column(DateTime, nullable=True, index=True)
    
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    
    source = Column(String(100), nullable=True)
    source_id = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    saved_by = relationship("SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan")


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    
    status = Column(String(50), default="saved")
    notes = Column(Text, nullable=True)
    
    saved_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by")
