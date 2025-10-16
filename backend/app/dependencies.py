from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import auth_service
from app.models.user import User
from app.config import settings

# Custom HTTPBearer that's optional in test mode
class OptionalHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        # In test mode, return None if no auth header
        if settings.USE_TEST_AUTH and settings.DEBUG:
            try:
                return await super().__call__(request)
            except:
                return None
        # In production, require auth
        return await super().__call__(request)

security = OptionalHTTPBearer(auto_error=False)

def get_test_user_from_db(db: Session) -> User:
    """Get or create test user for development"""
    test_user = db.query(User).filter(User.email == "test@mentorax.com").first()
    
    if not test_user:
        test_user = User(
            name="Test User",
            email="test@mentorax.com",
            auth0_id="test_auth0_id",
            degree="Computer Science",
            career_goal="Full Stack Developer"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    
    return test_user

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    In test mode (USE_TEST_AUTH=true), automatically returns test user
    """
    # TEST MODE: Return test user automatically
    if settings.USE_TEST_AUTH and settings.DEBUG:
        print("🔧 Test mode: Using test user")
        return get_test_user_from_db(db)
    
    # PRODUCTION MODE: Require valid token
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    token = credentials.credentials
    
    try:
        # Verify internal JWT token
        payload = auth_service.verify_token(token)
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency for optional authentication
    Returns user if authenticated, None otherwise
    """
    # Test mode: always return test user
    if settings.USE_TEST_AUTH and settings.DEBUG:
        return get_test_user_from_db(db)
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except:
        return None
