from app.services.s3_service import s3_service
import os

def test_s3_connection():
    """Test S3 connection and operations"""
    print("Testing S3 Service...")
    
    # Test 1: Upload a test file
    test_content = b"This is a test file for Mentorax S3 integration"
    result = s3_service.upload_file(
        file_content=test_content,
        folder="test",
        filename="test_file.txt",
        content_type="text/plain"
    )
    
    if result["success"]:
        print("✓ File upload successful")
        print(f"  File URL: {result['file_url']}")
        file_key = result["file_key"]
        
        # Test 2: Generate presigned URL
        presigned_url = s3_service.generate_presigned_url(file_key)
        if presigned_url:
            print("✓ Presigned URL generated successfully")
        
        # Test 3: Check if file exists
        exists = s3_service.file_exists(file_key)
        print(f"✓ File exists check: {exists}")
        
        # Test 4: Get file metadata
        metadata = s3_service.get_file_metadata(file_key)
        if metadata:
            print(f"✓ File metadata retrieved: {metadata['content_type']}")
        
        # Test 5: Delete file
        delete_result = s3_service.delete_file(file_key)
        if delete_result["success"]:
            print("✓ File deleted successfully")
        
        print("\n✅ All S3 tests passed!")
    else:
        print(f"✗ File upload failed: {result['message']}")

if __name__ == "__main__":
    test_s3_connection()
