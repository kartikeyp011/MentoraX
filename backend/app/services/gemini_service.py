import google.generativeai as genai
from app.config.settings import settings
import json
from typing import Optional, Dict, List, Any
import re

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API)
        
        # Initialize models
        self.text_model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation config
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
    
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text using Gemini"""
        try:
            response = self.text_model.generate_content(
                prompt,
                generation_config=kwargs.get('generation_config', self.generation_config),
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            print(f"Error generating text: {e}")
            return None
    
    def clean_json_response(self, text: str) -> str:
        """Clean JSON response from markdown and extra text"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Try to find complete JSON structure
        # First, try to find object (most common for our use case)
        brace_count = 0
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    end_idx = i + 1
                    break
        
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx]
        
        # If object not found, try array
        bracket_count = 0
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(text):
            if char == '[':
                if start_idx == -1:
                    start_idx = i
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and start_idx != -1:
                    end_idx = i + 1
                    break
        
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx]
        
        # If nothing found, return cleaned text
        return text.strip()
    
    def generate_json_response(self, prompt: str, max_retries: int = 2, **kwargs) -> Optional[Dict]:
        """Generate JSON response from Gemini with retry logic"""
        
        for attempt in range(max_retries):
            try:
                # Add JSON instruction to prompt
                json_prompt = f"""{prompt}

CRITICAL INSTRUCTIONS:
- Respond ONLY with valid JSON
- NO markdown formatting (no ```json or ```)
- NO explanations before or after the JSON
- Ensure all strings are properly escaped
- Use double quotes for all strings
- Ensure JSON is complete and valid
- Start response immediately with {{ or [
"""
                
                response = self.text_model.generate_content(
                    json_prompt,
                    generation_config=kwargs.get('generation_config', self.generation_config),
                    safety_settings=self.safety_settings
                )
                
                # Get text
                text = response.text.strip()
                
                # Clean the response
                cleaned_text = self.clean_json_response(text)
                
                # Parse JSON
                parsed = json.loads(cleaned_text)
                return parsed
                
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}/{max_retries} - JSON parsing error: {e}")
                if attempt == max_retries - 1:
                    print(f"Response text (first 500 chars): {text[:500] if 'text' in locals() else 'No text'}")
                    print(f"Cleaned text (first 500 chars): {cleaned_text[:500] if 'cleaned_text' in locals() else 'No cleaned text'}")
                continue
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} - Error: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    def start_chat(self, history: Optional[List[Dict]] = None) -> Any:
        """Start a chat session"""
        return self.chat_model.start_chat(history=history or [])
    
    def chat(self, chat_session: Any, message: str) -> Optional[str]:
        """Send message in chat session"""
        try:
            response = chat_session.send_message(
                message,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            print(f"Error in chat: {e}")
            return None
    
    # ========== Career Path Generation ==========
    
    def generate_career_paths(
        self,
        degree: str,
        skills: List[str],
        interests: List[str],
        career_goals: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """Generate personalized career paths"""
        
        skills_str = ", ".join(skills) if skills else "None specified"
        interests_str = ", ".join(interests) if interests else "None specified"
        goals_str = career_goals or "Open to exploring various options"
        
        # Use simpler direct request
        prompt = f"""Generate 5 different career paths for a student with:
    - Degree: {degree}
    - Skills: {skills_str}
    - Interests: {interests_str}
    - Goals: {goals_str}

    Response must be a JSON array starting with [ and ending with ].
    Each career path needs: role_title, description, required_skills (array), salary_range, growth_potential, learning_roadmap (array), estimated_time.

    Example structure:
    [
    {{"role_title": "Data Analyst", "description": "Analyze data", "required_skills": ["Python", "SQL"], "salary_range": "5-8 LPA", "growth_potential": "High", "learning_roadmap": ["Learn Python", "Learn SQL"], "estimated_time": "6 months"}},
    {{"role_title": "Web Developer", "description": "Build websites", "required_skills": ["HTML", "CSS", "JavaScript"], "salary_range": "4-7 LPA", "growth_potential": "High", "learning_roadmap": ["Learn HTML", "Learn CSS"], "estimated_time": "8 months"}}
    ]"""
        
        try:
            result = self.generate_json_response(prompt)
            
            if result:
                # If it's already a list, return it
                if isinstance(result, list):
                    return result
                # If it's a single object, wrap it in a list
                elif isinstance(result, dict):
                    print("Got single object, wrapping in array")
                    return [result]
            
            return None
        except Exception as e:
            print(f"Error in generate_career_paths: {e}")
            return None
    
    # ========== Skill Gap Analysis ==========
    
    def analyze_skill_gap(
        self,
        current_skills: List[str],
        target_role: str,
        experience_level: str = "entry"
    ) -> Optional[Dict]:
        """Analyze skill gaps for a target role"""
        
        skills_str = ", ".join(current_skills) if current_skills else "None"
        
        prompt = f"""Analyze the skill gap for becoming a {target_role} at {experience_level} level.

Current Skills: {skills_str}

You must return a single JSON object (not an array) with these exact keys:
{{
  "required_skills": ["skill1", "skill2"],
  "matching_skills": ["skill1"],
  "missing_skills": ["skill2"],
  "skill_gaps": [
    {{"skill": "Python", "current_proficiency": "Basic", "target_proficiency": "Intermediate"}}
  ],
  "priority_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "recommendations": [
    {{"skill": "JavaScript", "type": "Missing", "recommendation": "Take online course"}}
  ],
  "estimated_timeline": "3-6 months"
}}

Keep recommendations under 80 characters each. Include exactly 5 priority skills."""
        
        return self.generate_json_response(prompt)
    
    # ========== Degree to Career Mapping ==========
    
    def map_degree_to_careers(
        self,
        degree: str,
        specialization: Optional[str] = None
    ) -> Optional[Dict]:
        """Map degree to possible career options"""
        
        spec_str = f" with specialization in {specialization}" if specialization else ""
        
        prompt = f"""For a student with {degree}{spec_str}, provide career options.

Return JSON object with:
- technical_careers: array of 3 objects (title, description, avg_salary, required_skills array)
- non_technical_careers: array of 2 objects (same structure)
- entrepreneurship_options: array of 2 objects (same structure)
- emerging_fields: array of 2 objects (same structure)
- further_education: array of 2 objects (degree, description, career_boost)
- certifications: array of 3 objects (name, provider, value)

Keep descriptions under 100 characters."""
        
        return self.generate_json_response(prompt)
    
    # ========== Resume Analysis ==========
    
    def analyze_resume(self, resume_text: str) -> Optional[Dict]:
        """Analyze resume and provide feedback"""
        
        # Truncate if too long
        if len(resume_text) > 3000:
            resume_text = resume_text[:3000] + "..."
        
        prompt = f"""Analyze this resume and provide feedback:

{resume_text}

Return JSON object with:
- extracted_skills: array of strings
- experience_years: number
- education: string
- strengths: array of strings (3-5 points, each under 80 chars)
- weaknesses: array of strings (3-5 points, each under 80 chars)
- suggestions: array of strings (3-5 actionable items, each under 80 chars)
- ats_score: number (0-100)
- overall_rating: number (1-10)

Keep all points concise."""
        
        return self.generate_json_response(prompt)
    
    # ========== Resume Generation ==========
    
    def generate_resume_content(
        self,
        user_profile: Dict,
        target_role: Optional[str] = None
    ) -> Optional[Dict]:
        """Generate resume content"""
        
        target_str = f" for {target_role} role" if target_role else ""
        
        prompt = f"""Create resume content{target_str} for this profile:

Name: {user_profile.get('name')}
Degree: {user_profile.get('degree')}
Skills: {user_profile.get('skills')}

Return JSON object with:
- professional_summary: string (3-4 lines, under 300 chars)
- skills_section: object with technical (array), soft (array), tools (array)
- achievements: array of strings (3-5 points, each under 100 chars)
- keywords: array of strings (10-15 ATS-friendly keywords)

Be concise and impactful."""
        
        return self.generate_json_response(prompt)
    
    # ========== Interview Preparation ==========
    
    def generate_interview_questions(
        self,
        role: str,
        difficulty: str = "medium",
        count: int = 10
    ) -> Optional[List[Dict]]:
        """Generate interview questions for a role"""
        
        # Simplify for smaller count in testing
        actual_count = min(count, 5)
        
        prompt = f"""Generate {actual_count} interview questions for a {role} position at {difficulty} difficulty.

    Response must be a JSON array starting with [ and ending with ].
    Each question needs: question, type, ideal_answer_points (array), difficulty.

    Example structure:
    [
    {{"question": "What is OOP?", "type": "technical", "ideal_answer_points": ["Encapsulation", "Inheritance", "Polymorphism"], "difficulty": "easy"}},
    {{"question": "Explain REST API", "type": "technical", "ideal_answer_points": ["Stateless", "HTTP methods", "Resources"], "difficulty": "medium"}}
    ]"""
        
        try:
            result = self.generate_json_response(prompt)
            
            if result:
                # If it's already a list, return it
                if isinstance(result, list):
                    return result
                # If it's a single object, wrap it in a list
                elif isinstance(result, dict):
                    print("Got single object, wrapping in array")
                    return [result]
            
            return None
        except Exception as e:
            print(f"Error in generate_interview_questions: {e}")
            return None
    
    def evaluate_interview_answer(
        self,
        question: str,
        user_answer: str,
        ideal_answer_points: List[str]
    ) -> Optional[Dict]:
        """Evaluate a user's interview answer"""
        
        points_str = ", ".join(ideal_answer_points)
        
        prompt = f"""Evaluate this interview answer:

Question: {question}
Ideal points: {points_str}
User answer: {user_answer}

Return JSON object with:
- score: number (0-10)
- strengths: array of 2-3 strings (each under 80 chars)
- weaknesses: array of 2-3 strings (each under 80 chars)
- suggestions: array of 2-3 strings (each under 80 chars)

Be specific and constructive."""
        
        return self.generate_json_response(prompt)
    
    # ========== Learning Path Generation ==========
    
    def generate_learning_path(
        self,
        skill: str,
        current_level: str = "beginner",
        time_commitment: str = "flexible"
    ) -> Optional[Dict]:
        """Generate a learning path for a skill"""
        
        prompt = f"""Create learning path for {skill} (current level: {current_level}, time: {time_commitment}).

Return JSON object with:
- overview: string (under 200 chars)
- prerequisites: array of strings (3-5 items)
- learning_phases: array of 3-4 objects (title, duration, topics array, resources array)
- projects: array of 3 objects (title, description under 100 chars, difficulty)
- milestones: array of 5 strings
- estimated_timeline: string
- top_resources: array of 3 strings (course/book names)

Keep everything concise."""
        
        return self.generate_json_response(prompt)
    
    # ========== Sentiment Analysis ==========
    
    def analyze_sentiment(self, text: str) -> Optional[Dict]:
        """Analyze sentiment of text"""
        
        prompt = f"""Analyze sentiment of this text:

"{text}"

Return JSON object with:
- sentiment: string (positive/negative/neutral)
- sentiment_score: number (-1 to 1, one decimal)
- emotions: array of 2-4 strings (detected emotions)
- concerns: array of strings (any concerns detected)
- stress_level: string (low/medium/high)
- suggestions: array of 2-3 strings (supportive advice, each under 100 chars)

Be supportive and constructive."""
        
        return self.generate_json_response(prompt)
    
    # ========== Job Simulator ==========
    
    def generate_job_task(
        self,
        role: str,
        difficulty: str = "medium"
    ) -> Optional[Dict]:
        """Generate a realistic job task"""
        
        prompt = f"""Create a realistic {difficulty} difficulty task for {role}.

Return JSON object with:
- task_title: string (under 50 chars)
- scenario: string (under 200 chars)
- task_description: string (under 300 chars)
- requirements: array of 3-5 strings (deliverables)
- evaluation_criteria: array of 4-5 strings (how it will be judged)
- time_estimate: string (e.g., "2-3 hours")
- tips: array of 2-3 strings (helpful hints)

Be realistic and specific."""
        
        return self.generate_json_response(prompt)
    
    def evaluate_job_task_submission(
        self,
        task_description: str,
        submission: str,
        evaluation_criteria: List[str]
    ) -> Optional[Dict]:
        """Evaluate a job task submission"""
        
        criteria_str = ", ".join(evaluation_criteria)
        
        # Truncate if too long
        if len(submission) > 2000:
            submission = submission[:2000] + "..."
        
        prompt = f"""Evaluate this job task submission:

Task: {task_description}
Criteria: {criteria_str}
Submission: {submission}

Return JSON object with:
- overall_score: number (0-100)
- strengths: array of 2-3 strings (each under 100 chars)
- areas_for_improvement: array of 2-3 strings (each under 100 chars)
- feedback: string (under 300 chars)
- job_readiness_score: number (0-100)

Be constructive and specific."""
        
        return self.generate_json_response(prompt)

# Create singleton instance
gemini_service = GeminiService()
