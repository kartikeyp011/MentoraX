from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum
from datetime import datetime
from app.config.database import Base
import enum

class ResourceType(enum.Enum):
    VIDEO = "video"
    ARTICLE = "article"
    COURSE = "course"
    BOOK = "book"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"

class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    
    type = Column(Enum(ResourceType), nullable=False, index=True)
    difficulty = Column(Enum(DifficultyLevel), nullable=True, index=True)
    
    skills = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    author = Column(String(255), nullable=True)
    platform = Column(String(100), nullable=True)
    duration = Column(String(50), nullable=True)
    is_free = Column(Boolean, default=True)
    
    rating = Column(Integer, nullable=True)
    view_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    is_curated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
