from fastapi import APIRouter, HTTPException, Header
from backend.models import CareerPathRequest
from backend.database import fetch_one, fetch_all
from backend.auth import verify_session
from backend.faiss_utils import search_faiss
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API'))

router = APIRouter(prefix="/career", tags=["Career Guidance"])


def get_user_profile(user_id):
    """Get complete user profile with skills"""
    user = fetch_one(
        "SELECT user_id, name, email, degree, career_goal FROM users WHERE user_id = %s",
        (user_id,)
    )

    if not user:
        return None

    # Get user skills
    skills = fetch_all("""
                       SELECT s.skill_id, s.skill_name, us.proficiency
                       FROM user_skills us
                                JOIN skills s ON us.skill_id = s.skill_id
                       WHERE us.user_id = %s
                       """, (user_id,))

    user['skills'] = skills
    return user


@router.post("/path")
async def get_career_path(request: CareerPathRequest, authorization: str = Header(None)):
    """Get AI-powered career path recommendations"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    response_text = ""  # Initialize at function scope

    try:
        # Get user profile
        profile = get_user_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        # Prepare data for Gemini
        skill_names = [s['skill_name'] for s in profile['skills']] if profile['skills'] else []
        degree = profile.get('degree') or 'Not specified'
        career_goal = profile.get('career_goal') or 'Exploring options'

        # Build prompt
        prompt = f"""You are a career guidance counselor for college students. Analyze this student profile and provide career recommendations.

Student Profile:
- Degree/Major: {degree}
- Current Skills: {', '.join(skill_names) if skill_names else 'No skills listed yet'}
- Career Goal: {career_goal}

Task: Suggest 3 realistic career paths that match this profile. For each path, provide:
1. Career title (specific job role)
2. Why it fits their profile (2-3 sentences)
3. Missing skills they need to develop (list 3-4 specific skills)
4. Learning roadmap (4 actionable steps)

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "title": "Career Title",
    "fit_reason": "Explanation of why this fits...",
    "missing_skills": ["Skill 1", "Skill 2", "Skill 3"],
    "roadmap": ["Step 1", "Step 2", "Step 3", "Step 4"]
  }}
]

Be specific, practical, and encouraging. Focus on careers achievable for college students and recent graduates.
Important: Return ONLY the JSON array, no other text."""

        # Call Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        # Get response text
        response_text = response.text.strip()

        # Log the response for debugging
        print(f"Gemini API Response: {response_text[:200]}...")

        # Extract JSON from response (remove markdown code blocks if present)
        if '```json' in response_text:
            # Extract content between ```json and ```
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            # Extract content between first ``` and next ```
            parts = response_text.split('```')
            if len(parts) >= 2:
                response_text = parts[1].strip()

        # Try to parse JSON
        try:
            career_paths = json.loads(response_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to find JSON array in text
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                career_paths = json.loads(json_match.group(0))
            else:
                raise json.JSONDecodeError("No valid JSON array found", response_text, 0)

        # Validate the structure
        if not isinstance(career_paths, list) or len(career_paths) == 0:
            raise ValueError("Invalid career paths format")

        # Ensure each path has required fields
        for path in career_paths:
            if not all(key in path for key in ['title', 'fit_reason', 'missing_skills', 'roadmap']):
                raise ValueError("Missing required fields in career path")

        return {
            "success": True,
            "profile": {
                "degree": degree,
                "skills": skill_names,
                "career_goal": career_goal
            },
            "career_paths": career_paths
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")

        # Return a fallback response
        return {
            "success": True,
            "profile": {
                "degree": profile.get('degree') or 'Not specified',
                "skills": skill_names if 'skill_names' in locals() else [],
                "career_goal": profile.get('career_goal') or 'Exploring options'
            },
            "career_paths": [
                {
                    "title": "Software Developer",
                    "fit_reason": "Based on your profile, software development is a strong match. This role combines technical skills with problem-solving abilities.",
                    "missing_skills": ["Advanced Programming", "System Design", "Version Control (Git)"],
                    "roadmap": [
                        "Complete a full-stack web development course",
                        "Build 3-5 portfolio projects showcasing your skills",
                        "Contribute to open-source projects on GitHub",
                        "Practice coding interview questions on LeetCode"
                    ]
                },
                {
                    "title": "Data Analyst",
                    "fit_reason": "Your analytical mindset and interest in data make this a viable career path. Data analysts are in high demand across industries.",
                    "missing_skills": ["SQL", "Data Visualization (Tableau/PowerBI)", "Statistical Analysis"],
                    "roadmap": [
                        "Learn SQL and practice with real datasets",
                        "Master Excel and a visualization tool",
                        "Complete online courses in statistics and data analysis",
                        "Work on data analysis projects using public datasets"
                    ]
                },
                {
                    "title": "Product Manager",
                    "fit_reason": "This role bridges technology and business, perfect for those who understand tech but want to focus on strategy and user needs.",
                    "missing_skills": ["Product Strategy", "User Research", "Agile Methodologies"],
                    "roadmap": [
                        "Study product management frameworks and principles",
                        "Learn about user research and UX design basics",
                        "Work on a side project managing a small product",
                        "Network with product managers and attend PM meetups"
                    ]
                }
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error generating career path: {e}")
        print(f"Response text (if available): {response_text if response_text else 'No response'}")

        # Return fallback career paths
        return {
            "success": True,
            "profile": {
                "degree": "Computer Science",
                "skills": ["Python", "JavaScript"],
                "career_goal": "Tech Career"
            },
            "career_paths": [
                {
                    "title": "Software Engineer",
                    "fit_reason": "Software engineering is one of the most versatile and in-demand tech careers. Your technical background makes this an excellent fit.",
                    "missing_skills": ["Data Structures & Algorithms", "System Design", "Cloud Technologies"],
                    "roadmap": [
                        "Master data structures and algorithms",
                        "Build full-stack projects for your portfolio",
                        "Learn cloud platforms like AWS or Azure",
                        "Practice technical interviews regularly"
                    ]
                },
                {
                    "title": "DevOps Engineer",
                    "fit_reason": "DevOps combines development and operations, focusing on automation and efficiency. Great for those who like both coding and infrastructure.",
                    "missing_skills": ["Docker & Kubernetes", "CI/CD Pipelines", "Cloud Infrastructure"],
                    "roadmap": [
                        "Learn containerization with Docker",
                        "Study CI/CD tools like Jenkins or GitHub Actions",
                        "Get certified in a cloud platform",
                        "Set up automated deployment pipelines"
                    ]
                },
                {
                    "title": "Machine Learning Engineer",
                    "fit_reason": "ML engineering is at the cutting edge of technology. If you're interested in AI and data, this is an exciting career path.",
                    "missing_skills": ["Deep Learning", "MLOps", "Model Deployment"],
                    "roadmap": [
                        "Complete advanced ML courses and specializations",
                        "Build and deploy ML models in production",
                        "Learn MLOps practices and tools",
                        "Contribute to ML projects and competitions"
                    ]
                }
            ]
        }


@router.post("/skills/analyze")
async def analyze_skills(authorization: str = Header(None)):
    """Analyze user skills and suggest improvements using FAISS"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        profile = get_user_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        user_skill_ids = [s['skill_id'] for s in profile['skills']] if profile['skills'] else []

        # Get all skills
        all_skills = fetch_all("SELECT skill_id, skill_name FROM skills")

        # Find skills user doesn't have
        missing_skills = [s for s in all_skills if s['skill_id'] not in user_skill_ids]

        # Use FAISS to find relevant skills based on career goal
        career_goal = profile.get('career_goal') or profile.get('degree') or 'software development'
        relevant_skills = search_faiss(career_goal, index_type='skills', top_k=5)

        # Combine and recommend top 5 missing skills
        recommended = []
        for skill in relevant_skills:
            skill_id = int(skill['id'])
            if skill_id not in user_skill_ids:
                recommended.append({
                    'skill_id': skill_id,
                    'skill_name': skill['skill_name'],
                    'relevance': 'High' if skill['distance'] < 1.0 else 'Medium'
                })

        # If not enough from FAISS, add some random missing skills
        if len(recommended) < 5:
            for skill in missing_skills[:5 - len(recommended)]:
                if skill['skill_id'] not in [r['skill_id'] for r in recommended]:
                    recommended.append({
                        'skill_id': skill['skill_id'],
                        'skill_name': skill['skill_name'],
                        'relevance': 'Medium'
                    })

        return {
            "success": True,
            "current_skills": profile['skills'],
            "recommended_skills": recommended[:5],
            "message": "Based on your profile and career goals"
        }

    except Exception as e:
        print(f"Error analyzing skills: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing skills: {str(e)}")


@router.get("/degree/map")
async def map_degree_to_careers(degree: str):
    """Map a degree to potential career options"""
    try:
        prompt = f"""List 5 specific job roles/career paths for someone with a {degree} degree.

Return ONLY a valid JSON array of strings:
["Career 1", "Career 2", "Career 3", "Career 4", "Career 5"]

Be specific with job titles (e.g., "Machine Learning Engineer" not just "Engineer")."""

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        # Extract JSON safely from response
        response_text = response.strip()

        # Remove code fences if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1]
            response_text = response_text.split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1]
            response_text = response_text.split("```")[0].strip()

        career_paths = json.loads(response_text)

        return {
            "success": True,
            "degree": degree,
            "career_options": career_paths
        }

    except Exception as e:
        print(f"Error mapping degree: {e}")
        raise HTTPException(status_code=500, detail=f"Error mapping degree: {str(e)}")