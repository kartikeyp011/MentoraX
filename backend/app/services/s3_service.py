import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings
import uuid
import os
from typing import Optional
import mimetypes

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_file(
        self, 
        file_content: bytes, 
        folder: str, 
        filename: str,
        content_type: Optional[str] = None
    ) -> dict:
        """
        Upload a file to S3
        
        Args:
            file_content: File content as bytes
            folder: Folder path (e.g., 'resumes', 'portfolios', 'profile_pictures')
            filename: Original filename
            content_type: MIME type of file
            
        Returns:
            dict with file_key and file_url
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_key = f"{folder}/{unique_filename}"
            
            # Determine content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            
            return {
                "success": True,
                "file_key": file_key,
                "file_url": file_url,
                "message": "File uploaded successfully"
            }
            
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload file"
            }
    
    def upload_user_file(
        self,
        file_content: bytes,
        user_id: int,
        file_type: str,  # 'resume', 'portfolio', 'profile_picture'
        filename: str,
        content_type: Optional[str] = None
    ) -> dict:
        """Upload user-specific file with organized folder structure"""
        folder = f"{file_type}/{user_id}"
        return self.upload_file(file_content, folder, filename, content_type)
    
    def generate_presigned_url(
        self, 
        file_key: str, 
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for secure file access
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if error
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
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, file_key: str) -> dict:
        """
        Delete a file from S3
        
        Args:
            file_key: S3 object key
            
        Returns:
            dict with success status
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                "success": True,
                "message": "File deleted successfully"
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete file"
            }
    
    def get_file(self, file_key: str) -> Optional[bytes]:
        """
        Download file content from S3
        
        Args:
            file_key: S3 object key
            
        Returns:
            File content as bytes or None if error
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error getting file: {e}")
            return None
    
    def list_user_files(self, user_id: int, file_type: str) -> list:
        """
        List all files for a user in a specific category
        
        Args:
            user_id: User ID
            file_type: Type of files ('resume', 'portfolio', 'profile_picture')
            
        Returns:
            List of file information
        """
        try:
            prefix = f"{file_type}/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{obj['Key']}"
                    })
            
            return files
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, file_key: str) -> Optional[dict]:
        """
        Get file metadata from S3
        
        Args:
            file_key: S3 object key
            
        Returns:
            File metadata dict or None if error
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat(),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            print(f"Error getting file metadata: {e}")
            return None

# Create singleton instance
s3_service = S3Service()
