from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Resource(Base):
    __tablename__ = "resources"
    
    resource_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=True)  # course, video, article, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("ResourceSkill", back_populates="resource", cascade="all, delete-orphan")


class ResourceSkill(Base):
    __tablename__ = "resource_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    resource = relationship("Resource", back_populates="skills")
    skill = relationship("Skill", back_populates="resource_skills")
