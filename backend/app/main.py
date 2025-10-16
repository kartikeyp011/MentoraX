from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.middleware import setup_cors
from app.api import auth, user, career, coach, opportunities, learning  # Add learning
from app.utils.scheduler import start_scheduler, stop_scheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mentorax API",
    description="AI-powered career guidance and student growth platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS
setup_cors(app)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(career.router)
app.include_router(coach.router)
app.include_router(opportunities.router)
app.include_router(learning.router)  # Add learning router

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Mentorax API",
        "docs": "/docs",
        "health": "/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting Mentorax API in {settings.APP_ENV} mode")
    logger.info(f"Allowed origins: {settings.origins_list}")
    
    # Start scheduler for daily scraping
    if settings.APP_ENV == "production":
        start_scheduler()
        logger.info("Scraper scheduler started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down Mentorax API")
    
    # Stop scheduler
    if settings.APP_ENV == "production":
        stop_scheduler()
        logger.info("Scraper scheduler stopped")
