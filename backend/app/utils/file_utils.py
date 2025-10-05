import os
from typing import Tuple, Optional

# Allowed file extensions
ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.doc', '.docx'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_PORTFOLIO_EXTENSIONS = {'.pdf', '.html', '.zip'}

# Max file sizes (in bytes)
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024   # 2 MB
MAX_PORTFOLIO_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Check if file size is within limit"""
    return file_size <= max_size

def validate_resume(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate resume file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file_extension(filename, ALLOWED_RESUME_EXTENSIONS):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_RESUME_EXTENSIONS)}"
    
    if not validate_file_size(file_size, MAX_RESUME_SIZE):
        return False, f"File too large. Max size: {MAX_RESUME_SIZE / (1024*1024)}MB"
    
    return True, None

def validate_image(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate image file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file_extension(filename, ALLOWED_IMAGE_EXTENSIONS):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    if not validate_file_size(file_size, MAX_IMAGE_SIZE):
        return False, f"File too large. Max size: {MAX_IMAGE_SIZE / (1024*1024)}MB"
    
    return True, None

def validate_portfolio(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate portfolio file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file_extension(filename, ALLOWED_PORTFOLIO_EXTENSIONS):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_PORTFOLIO_EXTENSIONS)}"
    
    if not validate_file_size(file_size, MAX_PORTFOLIO_SIZE):
        return False, f"File too large. Max size: {MAX_PORTFOLIO_SIZE / (1024*1024)}MB"
    
    return True, None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename"""
    # Remove path separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized
