from sqlalchemy import Column, Integer, String, DateTime, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    opportunity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String(255), nullable=False)
    source = Column(String(50), nullable=True)  # LinkedIn, Glassdoor, etc.
    location = Column(String(100), nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("OpportunitySkill", back_populates="opportunity", cascade="all, delete-orphan")
    saved_by = relationship("SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="skills")
    skill = relationship("Skill", back_populates="opportunity_skills")


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by")
