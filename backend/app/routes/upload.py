from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.s3_service import s3_service
from app.utils.file_utils import (
    validate_resume, 
    validate_image, 
    validate_portfolio,
    sanitize_filename
)
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/resume/{user_id}")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload user resume to S3"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file
    is_valid, error_message = validate_resume(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Upload to S3
    result = s3_service.upload_user_file(
        file_content=file_content,
        user_id=user_id,
        file_type="resumes",
        filename=safe_filename,
        content_type=file.content_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update user's resume URL in database
    user.resume_url = result["file_url"]
    db.commit()
    
    return {
        "message": "Resume uploaded successfully",
        "file_url": result["file_url"],
        "file_key": result["file_key"]
    }

@router.post("/profile-picture/{user_id}")
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload user profile picture to S3"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file
    is_valid, error_message = validate_image(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Upload to S3
    result = s3_service.upload_user_file(
        file_content=file_content,
        user_id=user_id,
        file_type="profile_pictures",
        filename=safe_filename,
        content_type=file.content_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update user's profile picture URL in database
    user.profile_picture = result["file_url"]
    db.commit()
    
    return {
        "message": "Profile picture uploaded successfully",
        "file_url": result["file_url"],
        "file_key": result["file_key"]
    }

@router.post("/portfolio/{user_id}")
async def upload_portfolio(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload user portfolio to S3"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file
    is_valid, error_message = validate_portfolio(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Upload to S3
    result = s3_service.upload_user_file(
        file_content=file_content,
        user_id=user_id,
        file_type="portfolios",
        filename=safe_filename,
        content_type=file.content_type
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update user's portfolio URL in database
    user.portfolio_url = result["file_url"]
    db.commit()
    
    return {
        "message": "Portfolio uploaded successfully",
        "file_url": result["file_url"],
        "file_key": result["file_key"]
    }

@router.delete("/file")
async def delete_file(
    file_key: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a file from S3"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify user owns this file (check if file_key contains user_id)
    if f"/{user_id}/" not in file_key:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this file")
    
    # Delete from S3
    result = s3_service.delete_file(file_key)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update user's URLs if necessary
    if user.resume_url and file_key in user.resume_url:
        user.resume_url = None
    if user.profile_picture and file_key in user.profile_picture:
        user.profile_picture = None
    if user.portfolio_url and file_key in user.portfolio_url:
        user.portfolio_url = None
    
    db.commit()
    
    return {"message": "File deleted successfully"}

@router.get("/presigned-url")
async def get_presigned_url(file_key: str, expiration: int = 3600):
    """Generate presigned URL for secure file access"""
    url = s3_service.generate_presigned_url(file_key, expiration)
    
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")
    
    return {"presigned_url": url, "expires_in": expiration}
