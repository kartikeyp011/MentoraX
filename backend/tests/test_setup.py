import sys
print("Python version:", sys.version)

try:
    import fastapi
    print("✓ FastAPI installed")
except ImportError:
    print("✗ FastAPI not installed")

try:
    import sqlalchemy
    print("✓ SQLAlchemy installed")
except ImportError:
    print("✗ SQLAlchemy not installed")

try:
    import google.generativeai as genai
    print("✓ Gemini API installed")
except ImportError:
    print("✗ Gemini API not installed")

try:
    import faiss
    print("✓ FAISS installed")
except ImportError:
    print("✗ FAISS not installed")

try:
    import boto3
    print("✓ Boto3 (AWS SDK) installed")
except ImportError:
    print("✗ Boto3 not installed")

print("\nAll core dependencies checked!")
