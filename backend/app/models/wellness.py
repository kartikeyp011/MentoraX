from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class MentalHealthLog(Base):
    __tablename__ = "mental_health_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    mood_rating = Column(Integer, nullable=True)
    stress_level = Column(Integer, nullable=True)
    energy_level = Column(Integer, nullable=True)
    
    check_in_text = Column(Text, nullable=True)
    
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    detected_concerns = Column(JSON, nullable=True)
    
    ai_suggestions = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="mental_health_logs")
