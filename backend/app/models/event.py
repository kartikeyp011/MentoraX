from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum
from datetime import datetime
from app.config.database import Base
import enum

class EventType(enum.Enum):
    HACKATHON = "hackathon"
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    COMPETITION = "competition"
    CONFERENCE = "conference"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(EventType), nullable=False, index=True)
    
    organizer = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=False)
    
    start_date = Column(DateTime, nullable=True, index=True)
    end_date = Column(DateTime, nullable=True)
    registration_deadline = Column(DateTime, nullable=True, index=True)
    
    registration_url = Column(String(500), nullable=True)
    is_registration_open = Column(Boolean, default=True)
    
    prizes = Column(JSON, nullable=True)
    benefits = Column(JSON, nullable=True)
    
    tags = Column(JSON, nullable=True)
    difficulty = Column(String(50), nullable=True)
    
    source = Column(String(100), nullable=True)
    source_id = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
