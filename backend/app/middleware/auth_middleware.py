from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import auth_service

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional: Global authentication middleware
    Currently we use dependencies for auth, but this is here if needed
    """
    
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Continue to next middleware/endpoint
        response = await call_next(request)
        return response
