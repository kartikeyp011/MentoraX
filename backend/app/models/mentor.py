from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base
import enum

class MentorStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    INACTIVE = "inactive"

class Mentor(Base):
    __tablename__ = "mentors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    current_role = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    
    expertise_areas = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    industries = Column(JSON, nullable=True)
    
    bio = Column(Text, nullable=True)
    mentoring_capacity = Column(Integer, default=5)
    current_mentees = Column(Integer, default=0)
    
    is_available = Column(Boolean, default=True)
    preferred_communication = Column(JSON, nullable=True)
    
    status = Column(Enum(MentorStatus), default=MentorStatus.PENDING, index=True)
    linkedin_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    connections = relationship("MentorshipConnection", foreign_keys="[MentorshipConnection.mentor_id]", back_populates="mentor")


class ConnectionStatus(enum.Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

class MentorshipConnection(Base):
    __tablename__ = "mentorship_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False, index=True)
    
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.REQUESTED, index=True)
    request_message = Column(Text, nullable=True)
    focus_areas = Column(JSON, nullable=True)
    
    sessions_completed = Column(Integer, default=0)
    next_session = Column(DateTime, nullable=True)
    
    student_feedback = Column(Text, nullable=True)
    mentor_feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("User", foreign_keys=[student_id], back_populates="mentorship_requests")
    mentor = relationship("Mentor", foreign_keys=[mentor_id], back_populates="connections")
