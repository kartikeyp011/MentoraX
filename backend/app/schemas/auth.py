from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class Auth0Token(BaseModel):
    """Auth0 token from frontend"""
    token: str = Field(..., description="Auth0 JWT token")

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    """Login request with Auth0 token"""
    auth0_token: str

class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    user: dict

class LogoutResponse(BaseModel):
    """Logout response"""
    success: bool
    message: str
