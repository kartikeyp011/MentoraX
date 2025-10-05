from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str
    
    # Gemini API
    GEMINI_API: str
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Application
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")

    GEMINI_API:str = os.getenv("GEMINI_API")
    
    # S3 Folder Structure
    S3_RESUME_FOLDER: str = "resumes"
    S3_PORTFOLIO_FOLDER: str = "portfolios"
    S3_PROFILE_PICTURE_FOLDER: str = "profile-pictures"
    S3_MEDIA_FOLDER: str = "media"
    
    # File Upload Limits
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_RESUME_EXTENSIONS: list = [".pdf", ".docx", ".doc"]
    ALLOWED_IMAGE_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Presigned URL Expiration (in seconds)
    PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour

settings = Settings()
