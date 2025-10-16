from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    resume_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=True)
    embedding = Column(LargeBinary, nullable=True)  # Store FAISS embedding if needed
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
