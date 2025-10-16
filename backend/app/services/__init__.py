from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.services.s3_service import s3_service
from app.services.ai_service import ai_service
from app.services.opportunity_service import opportunity_service
from app.services.scraper_service import scraper_service
from app.services.resource_service import resource_service
from app.services.faiss_service import faiss_service

__all__ = [
    "auth_service",
    "user_service",
    "s3_service",
    "ai_service",
    "opportunity_service",
    "scraper_service",
    "resource_service",
    "faiss_service"
]
