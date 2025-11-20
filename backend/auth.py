from fastapi import APIRouter, HTTPException, Header
from .models import UserSignup, UserLogin
from .database import execute_query, fetch_one, fetch_all
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_session_token() -> str:
    """Generate unique session token"""
    return str(uuid.uuid4())


def verify_session(token: str) -> Optional[int]:
    """Verify session token and return user_id"""
    query = """
            SELECT user_id, expires_at
            FROM sessions
            WHERE session_token = %s \
            """
    session = fetch_one(query, (token,))

    if not session:
        return None

    # Check if session expired
    if session['expires_at'] < datetime.now():
        # Delete expired session
        execute_query("DELETE FROM sessions WHERE session_token = %s", (token,))
        return None

    return session['user_id']


@router.post("/signup")
async def signup(user: UserSignup):
    """Register a new user"""
    try:
        # Check if email already exists
        existing_user = fetch_one("SELECT email FROM users WHERE email = %s", (user.email,))
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        hashed_pw = hash_password(user.password)

        # Insert user
        query = """
                INSERT INTO users (name, email, password, degree, career_goal)
                VALUES (%s, %s, %s, %s, %s) \
                """
        user_id = execute_query(
            query,
            (user.name, user.email, hashed_pw, user.degree, user.career_goal)
        )

        # Create session
        session_token = create_session_token()
        expires_at = datetime.now() + timedelta(days=7)

        execute_query(
            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
            (user_id, session_token, expires_at)
        )

        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id,
            "session_token": session_token
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
async def login(credentials: UserLogin):
    """Login user"""
    try:
        # Hash the provided password
        hashed_pw = hash_password(credentials.password)

        # Check credentials
        query = "SELECT user_id, name FROM users WHERE email = %s AND password = %s"
        user = fetch_one(query, (credentials.email, hashed_pw))

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create session
        session_token = create_session_token()
        expires_at = datetime.now() + timedelta(days=7)

        execute_query(
            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
            (user['user_id'], session_token, expires_at)
        )

        return {
            "success": True,
            "message": "Login successful",
            "user_id": user['user_id'],
            "name": user['name'],
            "session_token": session_token
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout(authorization: str = Header(None)):
    """Logout user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No session token provided")

    try:
        # Extract token (format: "Bearer <token>")
        token = authorization.replace("Bearer ", "")

        # Delete session
        execute_query("DELETE FROM sessions WHERE session_token = %s", (token,))

        return {"success": True, "message": "Logged out successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.get("/verify")
async def verify_token(authorization: str = Header(None)):
    """Verify if session token is valid"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No session token provided")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"success": True, "user_id": user_id}