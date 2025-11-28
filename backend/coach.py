from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.database import fetch_one, fetch_all, execute_query
from backend.auth import verify_session
from backend.faiss_utils import search_faiss
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re
from typing import List

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

router = APIRouter(prefix="/coach", tags=["Upskill Coach"])


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []


def get_user_context(user_id):
    """Get user profile for context"""
    user = fetch_one(
        "SELECT name, degree, career_goal FROM users WHERE user_id = %s",
        (user_id,)
    )

    if not user:
        return None

    # Get skills
    skills = fetch_all("""
                       SELECT s.skill_name, us.proficiency
                       FROM user_skills us
                                JOIN skills s ON us.skill_id = s.skill_id
                       WHERE us.user_id = %s
                       """, (user_id,))

    user['skills'] = skills or []
    return user


@router.post("/chat")
async def chat_with_coach(chat: ChatMessage, authorization: str = Header(None)):
    """Chat with AI coach"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Get user context
        user_context = get_user_context(user_id)

        if not user_context:
            raise HTTPException(status_code=404, detail="User not found")

        # Build context for AI
        skill_names = [s['skill_name'] for s in user_context['skills']]
        context = f"""You are MentoraX Coach, an AI career guidance assistant for college students.

Current Student Context:
- Name: {user_context['name']}
- Degree: {user_context.get('degree') or 'Not specified'}
- Career Goal: {user_context.get('career_goal') or 'Exploring options'}
- Current Skills: {', '.join(skill_names) if skill_names else 'No skills listed yet'}

Your Role:
- Provide personalized career and learning advice
- Be encouraging, supportive, and specific
- Suggest actionable next steps
- Recommend relevant courses and resources
- Help with skill development planning
- Answer career-related questions

Student's Question: {chat.message}

Instructions:
- Give a helpful, conversational response (2-3 paragraphs max)
- Be specific and actionable
- Reference their profile when relevant
- At the end, provide 2-3 follow-up suggestions as a JSON array

Return your response in this format:
{{
  "response": "Your detailed response here...",
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
}}

Return ONLY valid JSON, no other text."""

        # Call Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(context)

        response_text = response.text.strip()

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in text
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # Fallback response
                result = {
                    "response": response_text,
                    "suggestions": [
                        "Tell me more about your career goals",
                        "What skills would you like to develop?",
                        "Would you like a personalized learning plan?"
                    ]
                }

        return {
            "success": True,
            "response": result.get('response', response_text),
            "suggestions": result.get('suggestions', [])
        }

    except Exception as e:
        print(f"Coach chat error: {e}")
        # Fallback response
        return {
            "success": True,
            "response": "I'm here to help you with your career journey! I can assist with skill development, career planning, learning resources, and more. What would you like to know?",
            "suggestions": [
                "What skills should I learn for my career goal?",
                "Can you create a learning roadmap for me?",
                "What are the best resources for learning Python?"
            ]
        }


@router.get("/plan")
async def get_learning_plan(authorization: str = Header(None)):
    """Generate a personalized learning plan"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        user_context = get_user_context(user_id)

        if not user_context:
            raise HTTPException(status_code=404, detail="User not found")

        skill_names = [s['skill_name'] for s in user_context['skills']]

        # Find skill gaps and resources
        career_goal = user_context.get('career_goal') or user_context.get('degree') or 'software development'

        # Get all skills to find missing ones
        all_skills = fetch_all("SELECT skill_id, skill_name FROM skills")
        user_skill_ids = [s['skill_id'] for s in user_context['skills']]
        missing_skills = [s for s in all_skills if s['skill_id'] not in user_skill_ids]

        # Use FAISS to find relevant skills
        relevant_skills = search_faiss(career_goal, index_type='skills', top_k=5)

        # Get relevant resources
        resources = search_faiss(career_goal, index_type='resources', top_k=5)

        return {
            "success": True,
            "plan": {
                "current_skills": skill_names,
                "recommended_skills": [s['skill_name'] for s in relevant_skills[:3]],
                "learning_resources": [
                    {
                        "title": r['title'],
                        "description": r['description'],
                        "url": r['url']
                    } for r in resources[:3]
                ],
                "next_steps": [
                    "Review the recommended resources and pick one to start",
                    "Practice by building small projects",
                    "Join online communities related to your field",
                    "Apply for internships to gain practical experience"
                ]
            }
        }

    except Exception as e:
        print(f"Learning plan error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating learning plan: {str(e)}")


@router.get("/suggestions")
async def get_quick_suggestions():
    """Get quick suggestion prompts"""
    return {
        "success": True,
        "suggestions": [
            "What skills should I learn to become a software engineer?",
            "Create a 3-month learning plan for me",
            "How can I prepare for technical interviews?",
            "What are the best resources for learning machine learning?",
            "How do I choose between frontend and backend development?",
            "What certifications should I pursue?",
            "How can I build a strong portfolio?",
            "Tips for landing my first internship"
        ]
    }