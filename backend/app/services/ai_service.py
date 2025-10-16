import google.generativeai as genai
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for Gemini AI integration"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    async def generate_career_paths(
        self,
        user_profile: Dict,
        skills: List[str],
        degree: Optional[str] = None,
        career_interests: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate personalized career path recommendations
        """
        try:
            # Construct prompt
            prompt = self._build_career_path_prompt(
                user_profile, skills, degree, career_interests
            )
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response
            career_data = self._parse_career_response(response.text)
            
            return career_data
            
        except Exception as e:
            logger.error(f"Career path generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    def _build_career_path_prompt(
        self,
        user_profile: Dict,
        skills: List[str],
        degree: Optional[str],
        career_interests: Optional[List[str]]
    ) -> str:
        """Build prompt for career path generation"""
        
        skills_str = ", ".join(skills) if skills else "None specified"
        interests_str = ", ".join(career_interests) if career_interests else "Not specified"
        degree_str = degree if degree else "Not specified"
        
        prompt = f"""
You are an expert career counselor. Analyze the following student profile and provide personalized career recommendations.

Student Profile:
- Name: {user_profile.get('name', 'Student')}
- Degree: {degree_str}
- Current Skills: {skills_str}
- Career Interests: {interests_str}
- Career Goal: {user_profile.get('career_goal', 'Not specified')}

Based on this profile, provide a detailed analysis in the following JSON format:

{{
    "career_options": [
        {{
            "title": "Career Title",
            "description": "Brief description of the role",
            "required_skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"],
            "salary_range": "$XX,XXX - $XX,XXX",
            "growth_potential": "high/medium/low",
            "match_percentage": 85
        }}
    ],
    "recommended_path": "Primary recommended career path with reasoning",
    "next_steps": ["Step 1", "Step 2", "Step 3"],
    "learning_recommendations": ["Course 1", "Course 2", "Certification 3"]
}}

Provide 3-5 career options ranked by match percentage. Be specific and actionable.
Return ONLY valid JSON, no additional text.
"""
        return prompt
    
    def _parse_career_response(self, response_text: str) -> Dict:
        """Parse AI response into structured data"""
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {response_text}")
            # Return fallback response
            return {
                "career_options": [],
                "recommended_path": "Unable to generate recommendations at this time.",
                "next_steps": ["Update your skills", "Complete your profile"],
                "learning_recommendations": []
            }
    
    async def analyze_skill_gaps(
        self,
        current_skills: List[str],
        target_role: str,
        resume_text: Optional[str] = None
    ) -> Dict:
        """
        Analyze skill gaps for a target role
        """
        try:
            prompt = self._build_skill_gap_prompt(
                current_skills, target_role, resume_text
            )
            
            response = self.model.generate_content(prompt)
            skill_gap_data = self._parse_skill_gap_response(response.text)
            
            return skill_gap_data
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    def _build_skill_gap_prompt(
        self,
        current_skills: List[str],
        target_role: str,
        resume_text: Optional[str]
    ) -> str:
        """Build prompt for skill gap analysis"""
        
        skills_str = ", ".join(current_skills) if current_skills else "None"
        resume_section = f"\n\nResume Summary:\n{resume_text}" if resume_text else ""
        
        prompt = f"""
You are a technical recruiter analyzing skill requirements. 

Current Skills: {skills_str}
Target Role: {target_role}{resume_section}

Analyze the skill gap and provide recommendations in this JSON format:

{{
    "current_skills": ["skill1", "skill2"],
    "missing_skills": [
        {{
            "skill_name": "Skill Name",
            "importance": "high/medium/low",
            "reason": "Why this skill is important for the role"
        }}
    ],
    "recommended_skills": [
        {{
            "skill_name": "Skill Name",
            "importance": "high/medium/low",
            "reason": "Why learning this would be beneficial"
        }}
    ],
    "learning_path": ["Step 1: Learn X", "Step 2: Practice Y", "Step 3: Build Z"]
}}

Focus on actionable, specific skills. Prioritize by importance.
Return ONLY valid JSON, no additional text.
"""
        return prompt
    
    def _parse_skill_gap_response(self, response_text: str) -> Dict:
        """Parse skill gap analysis response"""
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError:
            return {
                "current_skills": [],
                "missing_skills": [],
                "recommended_skills": [],
                "learning_path": []
            }
    
    async def map_degree_to_careers(
        self,
        degree: str,
        specialization: Optional[str] = None
    ) -> Dict:
        """
        Map a degree to potential career paths
        """
        try:
            prompt = self._build_degree_map_prompt(degree, specialization)
            response = self.model.generate_content(prompt)
            degree_data = self._parse_degree_map_response(response.text)
            
            return degree_data
            
        except Exception as e:
            logger.error(f"Degree mapping failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    def _build_degree_map_prompt(
        self,
        degree: str,
        specialization: Optional[str]
    ) -> str:
        """Build prompt for degree to career mapping"""
        
        spec_text = f" with specialization in {specialization}" if specialization else ""
        
        prompt = f"""
You are a career advisor specializing in degree-to-career mapping.

Degree: {degree}{spec_text}

Provide comprehensive career information in this JSON format:

{{
    "degree": "{degree}",
    "career_paths": [
        "Career Path 1",
        "Career Path 2",
        "Career Path 3",
        "Career Path 4",
        "Career Path 5"
    ],
    "top_skills": [
        "Essential Skill 1",
        "Essential Skill 2",
        "Essential Skill 3",
        "Essential Skill 4",
        "Essential Skill 5"
    ],
    "industry_trends": [
        "Current trend 1 in the field",
        "Emerging opportunity 2",
        "Future direction 3"
    ]
}}

Focus on realistic, current career options and in-demand skills.
Return ONLY valid JSON, no additional text.
"""
        return prompt
    
    def _parse_degree_map_response(self, response_text: str) -> Dict:
        """Parse degree mapping response"""
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError:
            return {
                "degree": degree,
                "career_paths": [],
                "top_skills": [],
                "industry_trends": []
            }
    
    async def generate_coach_response(
        self,
        user_message: str,
        user_context: Dict
    ) -> Dict:
        """
        Generate AI coach chat response
        """
        try:
            prompt = self._build_coach_prompt(user_message, user_context)
            response = self.model.generate_content(prompt)
            
            return {
                "response": response.text,
                "suggested_resources": [],  # Can be enhanced
                "action_items": self._extract_action_items(response.text)
            }
            
        except Exception as e:
            logger.error(f"Coach response generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    def _build_coach_prompt(
        self,
        user_message: str,
        user_context: Dict
    ) -> str:
        """Build prompt for AI coach"""
        
        skills = ", ".join(user_context.get('skills', []))
        
        prompt = f"""
You are Mentorax, an AI career coach helping students with their career development.

Student Context:
- Skills: {skills}
- Degree: {user_context.get('degree', 'Not specified')}
- Career Goal: {user_context.get('career_goal', 'Not specified')}

Student Question: {user_message}

Provide a helpful, encouraging, and actionable response. Be specific and personalized based on their context.
If relevant, suggest next steps or resources they should explore.
Keep the response conversational and supportive.
"""
        return prompt
    
    def _extract_action_items(self, response_text: str) -> List[str]:
        """Extract action items from response"""
        action_items = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered lists or bullet points
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*', '•')):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-*•').strip()
                if clean_line:
                    action_items.append(clean_line)
        
        return action_items[:5]  # Return max 5 action items
    
    async def generate_skill_plan(
        self,
        user_profile: Dict,
        current_skills: List[str],
        target_role: Optional[str],
        timeline: str = "3 months"
    ) -> Dict:
        """
        Generate personalized skill development plan
        """
        try:
            prompt = self._build_skill_plan_prompt(
                user_profile, current_skills, target_role, timeline
            )
            
            response = self.model.generate_content(prompt)
            plan_data = self._parse_skill_plan_response(response.text)
            
            return plan_data
            
        except Exception as e:
            logger.error(f"Skill plan generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    def _build_skill_plan_prompt(
        self,
        user_profile: Dict,
        current_skills: List[str],
        target_role: Optional[str],
        timeline: str
    ) -> str:
        """Build prompt for skill development plan"""
        
        skills_str = ", ".join(current_skills) if current_skills else "Beginner"
        target_str = target_role if target_role else user_profile.get('career_goal', 'general career development')
        
        prompt = f"""
You are a learning advisor creating a personalized skill development plan.

Student Profile:
- Current Skills: {skills_str}
- Target Role: {target_str}
- Timeline: {timeline}
- Degree: {user_profile.get('degree', 'Not specified')}

Create a detailed learning plan in this JSON format:

{{
    "plan_title": "Personalized Learning Plan for [Role]",
    "total_duration": "{timeline}",
    "steps": [
        {{
            "step_number": 1,
            "skill_name": "Skill Name",
            "description": "What to learn and why",
            "estimated_time": "2 weeks",
            "resources": [
                {{"type": "course", "name": "Course Name", "platform": "Platform"}},
                {{"type": "practice", "name": "Project/Exercise"}}
            ],
            "priority": "high/medium/low"
        }}
    ],
    "milestones": [
        "Week 4: Complete foundational courses",
        "Week 8: Build first project",
        "Week 12: Ready for interviews"
    ]
}}

Provide 5-8 learning steps prioritized by importance. Be realistic about time estimates.
Return ONLY valid JSON, no additional text.
"""
        return prompt
    
    def _parse_skill_plan_response(self, response_text: str) -> Dict:
        """Parse skill plan response"""
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError:
            return {
                "plan_title": "Custom Learning Plan",
                "total_duration": timeline,
                "steps": [],
                "milestones": []
            }

# Initialize service
ai_service = AIService()
