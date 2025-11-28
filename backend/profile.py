from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from backend.models import UpdateProfile, UserProfile
from backend.database import fetch_one, fetch_all, execute_query
from backend.auth import verify_session
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# AWS S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'  # Change if your bucket is in different region
)

BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')

router = APIRouter(prefix="/user", tags=["User Profile"])


def get_complete_profile(user_id):
    """Get complete user profile with skills"""
    user = fetch_one(
        "SELECT user_id, name, email, degree, career_goal, resume_url FROM users WHERE user_id = %s",
        (user_id,)
    )

    if not user:
        return None

    # Get user skills with proficiency
    skills = fetch_all("""
                       SELECT s.skill_id, s.skill_name, us.proficiency
                       FROM user_skills us
                                JOIN skills s ON us.skill_id = s.skill_id
                       WHERE us.user_id = %s
                       ORDER BY us.proficiency DESC
                       """, (user_id,))

    user['skills'] = skills or []
    return user


@router.get("/profile")
async def get_profile(authorization: str = Header(None)):
    """Get user profile"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        profile = get_complete_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "profile": profile
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")


@router.post("/update")
async def update_profile(profile_update: UpdateProfile, authorization: str = Header(None)):
    """Update user profile"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Update basic profile info
        update_fields = []
        params = []

        if profile_update.degree is not None:
            update_fields.append("degree = %s")
            params.append(profile_update.degree)

        if profile_update.career_goal is not None:
            update_fields.append("career_goal = %s")
            params.append(profile_update.career_goal)

        if update_fields:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
            params.append(user_id)
            execute_query(query, tuple(params))

        # Update skills
        if profile_update.skills is not None:
            # Delete existing skills
            execute_query("DELETE FROM user_skills WHERE user_id = %s", (user_id,))

            # Insert new skills
            for skill in profile_update.skills:
                execute_query(
                    "INSERT INTO user_skills (user_id, skill_id, proficiency) VALUES (%s, %s, %s)",
                    (user_id, skill['skill_id'], skill.get('proficiency', 3))
                )

        # Get updated profile
        updated_profile = get_complete_profile(user_id)

        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": updated_profile
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...), authorization: str = Header(None)):
    """Upload resume to AWS S3"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read file content
        file_content = await file.read()

        # Check file size (max 5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resumes/user_{user_id}_{timestamp}.pdf"

        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content,
            ContentType='application/pdf'
        )

        # Generate S3 URL
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

        # Update user record
        execute_query(
            "UPDATE users SET resume_url = %s WHERE user_id = %s",
            (s3_url, user_id)
        )

        return {
            "success": True,
            "message": "Resume uploaded successfully",
            "resume_url": s3_url
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"S3 upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")


@router.get("/skills/all")
async def get_all_skills():
    """Get all available skills"""
    try:
        skills = fetch_all("SELECT skill_id, skill_name, description FROM skills ORDER BY skill_name")
        return {
            "success": True,
            "skills": skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching skills: {str(e)}")


@router.get("/stats")
async def get_user_stats(authorization: str = Header(None)):
    """Get user statistics"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Count user skills
        skill_count = fetch_one(
            "SELECT COUNT(*) as count FROM user_skills WHERE user_id = %s",
            (user_id,)
        )['count']

        # Count saved opportunities
        saved_count = fetch_one(
            "SELECT COUNT(*) as count FROM saved_opportunities WHERE user_id = %s",
            (user_id,)
        )['count']

        return {
            "success": True,
            "stats": {
                "skills_count": skill_count,
                "saved_opportunities": saved_count,
                "completed_courses": 0  # Placeholder
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
