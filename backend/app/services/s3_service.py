import boto3
from botocore.exceptions import ClientError
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.models.resume import Resume
from datetime import datetime
import uuid

class S3Service:
    """Service for AWS S3 operations"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_resume(
        self,
        user_id: int,
        file_content: bytes,
        file_name: str,
        db: Session
    ) -> Resume:
        """
        Upload resume to S3 and create database record
        """
        try:
            # Generate unique file key
            file_extension = file_name.split('.')[-1]
            unique_filename = f"resumes/{user_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType='application/pdf'
            )
            
            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            
            # Create database record
            resume = Resume(
                user_id=user_id,
                file_url=file_url,
                file_name=file_name,
                uploaded_at=datetime.utcnow()
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            return resume
            
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 upload failed: {str(e)}"
            )
    
    async def delete_resume(
        self,
        resume_id: int,
        user_id: int,
        db: Session
    ):
        """
        Delete resume from S3 and database
        """
        # Get resume record
        resume = db.query(Resume).filter(
            Resume.resume_id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        try:
            # Extract S3 key from URL
            s3_key = resume.file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Delete from database
            db.delete(resume)
            db.commit()
            
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 delete failed: {str(e)}"
            )
    
    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate pre-signed URL for temporary access
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate pre-signed URL: {str(e)}"
            )

# Initialize service
s3_service = S3Service()
