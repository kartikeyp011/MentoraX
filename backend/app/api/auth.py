from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse
)
from app.services.auth_service import auth_service
from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with Auth0 token
    
    Flow:
    1. Frontend sends Auth0 token
    2. Backend verifies token with Auth0
    3. Get or create user in database
    4. Issue internal JWT token
    5. Return token to frontend
    """
    try:
        # Verify Auth0 token
        auth0_payload = await auth_service.verify_auth0_token(request.auth0_token)
        
        # Get or create user
        user = auth_service.get_or_create_user(auth0_payload, db)
        
        # Create internal access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "user_id": user.user_id,
                "email": user.email,
                "auth0_id": user.auth0_id
            },
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "degree": user.degree,
                "career_goal": user.career_goal
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so we can't truly "invalidate" them.
    Frontend should remove the token from storage.
    For enhanced security, implement token blacklisting with Redis.
    """
    return LogoutResponse(
        success=True,
        message=f"User {current_user.name} logged out successfully"
    )

@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify if current token is valid
    Useful for frontend to check authentication status
    """
    return {
        "valid": True,
        "user": {
            "user_id": current_user.user_id,
            "name": current_user.name,
            "email": current_user.email
        }
    }

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "degree": current_user.degree,
        "career_goal": current_user.career_goal,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
