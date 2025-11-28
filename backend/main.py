from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from . import auth, opportunities, career, profile, resources, coach

app = FastAPI(title="MentoraX API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="C:/Users/knpra/Desktop/MentoraX/frontend"), name="static")

# @app.get("/")
# async def root():
#     return {"status": "MentoraX API Running", "version": "1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve frontend pages
@app.get("/")
async def serve_landing():
    return FileResponse("frontend/landing.html")

@app.get("/login")
async def serve_login():
    return FileResponse("frontend/login.html")

@app.get("/signup")
async def serve_signup():
    return FileResponse("frontend/signup.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/career-guidance")
async def serve_career():
    return FileResponse("frontend/career_guidance.html")

@app.get("/profile")
async def serve_profile():
    return FileResponse("frontend/profile.html")

@app.get("/opportunities")
async def serve_opportunities():
    return FileResponse("frontend/opportunities.html")

@app.get("/learning-zone")
async def serve_learning_zone():
    return FileResponse("frontend/learning_zone.html")

@app.get("/upskill-coach")
async def serve_upskill_coach():
    return FileResponse("frontend/upskill_coach.html")

# Import and include routers (will add these next)
# from backend import auth, career, opportunities, profile, resources
app.include_router(auth.router)
app.include_router(career.router)
app.include_router(opportunities.router)
app.include_router(profile.router)
app.include_router(resources.router)
app.include_router(coach.router)