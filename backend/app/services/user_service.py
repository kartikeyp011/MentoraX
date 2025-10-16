from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.schemas.user import UserUpdate, UserProfileResponse, UserStatsResponse, SkillBase
from app.models.opportunity import SavedOpportunity
from datetime import datetime

class UserService:
    """Service for user-related operations"""
    
    def get_user_profile(self, user_id: int, db: Session) -> User:
        """Get user profile with skills"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    def update_user_profile(
        self, 
        user_id: int, 
        update_data: UserUpdate, 
        db: Session
    ) -> User:
        """Update user profile"""
        user = self.get_user_profile(user_id, db)
        
        # Update basic fields
        if update_data.name is not None:
            user.name = update_data.name
        if update_data.degree is not None:
            user.degree = update_data.degree
        if update_data.career_goal is not None:
            user.career_goal = update_data.career_goal
        
        user.updated_at = datetime.utcnow()
        
        # Update skills if provided
        if update_data.skills is not None:
            self._update_user_skills(user, update_data.skills, db)
        
        db.commit()
        db.refresh(user)
        return user
    
    def _update_user_skills(
        self, 
        user: User, 
        skills_data: List[SkillBase], 
        db: Session
    ):
        """Update user's skills"""
        # Remove existing skills
        db.query(UserSkill).filter(UserSkill.user_id == user.user_id).delete()
        
        # Add new skills
        for skill_data in skills_data:
            # Get or create skill
            skill = db.query(Skill).filter(
                Skill.skill_name == skill_data.skill_name
            ).first()
            
            if not skill:
                skill = Skill(skill_name=skill_data.skill_name)
                db.add(skill)
                db.flush()
            
            # Create user-skill relationship
            user_skill = UserSkill(
                user_id=user.user_id,
                skill_id=skill.skill_id,
                proficiency=skill_data.proficiency or 1
            )
            db.add(user_skill)
    
    def add_user_skill(
        self, 
        user_id: int, 
        skill_name: str, 
        proficiency: int, 
        db: Session
    ) -> UserSkill:
        """Add a single skill to user"""
        # Get or create skill
        skill = db.query(Skill).filter(Skill.skill_name == skill_name).first()
        if not skill:
            skill = Skill(skill_name=skill_name)
            db.add(skill)
            db.flush()
        
        # Check if user already has this skill
        existing = db.query(UserSkill).filter(
            UserSkill.user_id == user_id,
            UserSkill.skill_id == skill.skill_id
        ).first()
        
        if existing:
            # Update proficiency
            existing.proficiency = proficiency
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new user skill
        user_skill = UserSkill(
            user_id=user_id,
            skill_id=skill.skill_id,
            proficiency=proficiency
        )
        db.add(user_skill)
        db.commit()
        db.refresh(user_skill)
        return user_skill
    
    def remove_user_skill(
        self, 
        user_id: int, 
        skill_id: int, 
        db: Session
    ):
        """Remove a skill from user"""
        user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == user_id,
            UserSkill.skill_id == skill_id
        ).first()
        
        if not user_skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found for this user"
            )
        
        db.delete(user_skill)
        db.commit()
    
    def get_user_stats(self, user_id: int, db: Session) -> UserStatsResponse:
        """Get dashboard statistics for user"""
        user = self.get_user_profile(user_id, db)
        
        # Count skills
        total_skills = db.query(UserSkill).filter(
            UserSkill.user_id == user_id
        ).count()
        
        # Count saved opportunities
        saved_opportunities = db.query(SavedOpportunity).filter(
            SavedOpportunity.user_id == user_id
        ).count()
        
        # Calculate profile completion
        profile_completion = self._calculate_profile_completion(user)
        
        return UserStatsResponse(
            total_skills=total_skills,
            saved_opportunities=saved_opportunities,
            completed_resources=0,  # TODO: Implement resource tracking
            profile_completion=profile_completion
        )
    
    def _calculate_profile_completion(self, user: User) -> int:
        """Calculate profile completion percentage"""
        fields = [
            user.name,
            user.email,
            user.degree,
            user.career_goal,
            len(user.skills) > 0
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)
    
    def get_user_skills(self, user_id: int, db: Session) -> List[dict]:
        """Get all skills for a user with details"""
        user_skills = db.query(UserSkill).filter(
            UserSkill.user_id == user_id
        ).all()
        
        result = []
        for us in user_skills:
            skill = db.query(Skill).filter(
                Skill.skill_id == us.skill_id
            ).first()
            
            result.append({
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "description": skill.description,
                "proficiency": us.proficiency
            })
        
        return result

# Initialize service
user_service = UserService()
