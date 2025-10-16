from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

class AuthService:
    """Authentication service for Auth0 and JWT"""
    
    def __init__(self):
        self.auth0_domain = settings.AUTH0_DOMAIN
        self.api_audience = settings.AUTH0_API_AUDIENCE
        self.algorithms = [settings.AUTH0_ALGORITHMS]
        self.issuer = settings.AUTH0_ISSUER
        self.jwks_url = f"https://{self.auth0_domain}/.well-known/jwks.json"
    
    async def verify_auth0_token(self, token: str) -> Dict:
        """
        Verify Auth0 JWT token
        Returns decoded token payload if valid
        """
        try:
            # Get JWKS (JSON Web Key Set) from Auth0
            async with httpx.AsyncClient() as client:
                jwks_response = await client.get(self.jwks_url)
                jwks = jwks_response.json()
            
            # Get the key ID from token header
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=self.algorithms,
                audience=self.api_audience,
                issuer=self.issuer
            )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create internal JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """
        Verify internal JWT token
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_or_create_user(
        self, 
        auth0_payload: Dict, 
        db: Session
    ) -> User:
        """
        Get existing user or create new one from Auth0 payload
        """
        auth0_id = auth0_payload.get("sub")
        email = auth0_payload.get("email")
        name = auth0_payload.get("name") or email.split("@")[0]
        
        if not auth0_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Auth0 token payload"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.auth0_id == auth0_id).first()
        
        if not user:
            # Create new user
            user = User(
                auth0_id=auth0_id,
                email=email,
                name=name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user

# Initialize auth service
auth_service = AuthService()
