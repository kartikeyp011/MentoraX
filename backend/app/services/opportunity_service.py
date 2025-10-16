from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status
from datetime import datetime, date
from app.models.opportunity import Opportunity, OpportunitySkill, SavedOpportunity
from app.models.skill import Skill
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunityFilterRequest
)

class OpportunityService:
    """Service for opportunity management"""
    
    def get_all_opportunities(
        self,
        user_id: Optional[int],
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> tuple[List[Opportunity], int]:
        """
        Get all opportunities with pagination
        Returns: (opportunities, total_count)
        """
        query = db.query(Opportunity).order_by(desc(Opportunity.created_at))
        
        total = query.count()
        opportunities = query.limit(limit).offset(offset).all()
        
        # Mark saved opportunities if user is authenticated
        if user_id:
            self._mark_saved_opportunities(opportunities, user_id, db)
        
        return opportunities, total
    
    def filter_opportunities(
        self,
        filter_request: OpportunityFilterRequest,
        user_id: Optional[int],
        db: Session
    ) -> tuple[List[Opportunity], int]:
        """
        Filter opportunities based on criteria
        """
        query = db.query(Opportunity)
        
        # Filter by skills
        if filter_request.skills:
            skill_ids = db.query(Skill.skill_id).filter(
                Skill.skill_name.in_(filter_request.skills)
            ).all()
            skill_ids = [s[0] for s in skill_ids]
            
            if skill_ids:
                query = query.join(OpportunitySkill).filter(
                    OpportunitySkill.skill_id.in_(skill_ids)
                )
        
        # Filter by location
        if filter_request.location:
            query = query.filter(
                Opportunity.location.ilike(f"%{filter_request.location}%")
            )
        
        # Filter by source
        if filter_request.source:
            query = query.filter(
                Opportunity.source.ilike(f"%{filter_request.source}%")
            )
        
        # Filter by deadline
        if filter_request.deadline_before:
            query = query.filter(
                Opportunity.deadline <= filter_request.deadline_before
            )
        
        # Order by most recent
        query = query.order_by(desc(Opportunity.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        opportunities = query.limit(filter_request.limit).offset(filter_request.offset).all()
        
        # Mark saved opportunities
        if user_id:
            self._mark_saved_opportunities(opportunities, user_id, db)
        
        return opportunities, total
    
    def _mark_saved_opportunities(
        self,
        opportunities: List[Opportunity],
        user_id: int,
        db: Session
    ):
        """
        Mark which opportunities are saved by the user
        """
        opp_ids = [opp.opportunity_id for opp in opportunities]
        
        saved = db.query(SavedOpportunity.opportunity_id).filter(
            and_(
                SavedOpportunity.user_id == user_id,
                SavedOpportunity.opportunity_id.in_(opp_ids)
            )
        ).all()
        
        saved_ids = {s[0] for s in saved}
        
        for opp in opportunities:
            opp.is_saved = opp.opportunity_id in saved_ids
    
    def save_opportunity(
        self,
        user_id: int,
        opportunity_id: int,
        db: Session
    ) -> SavedOpportunity:
        """
        Save/bookmark an opportunity for a user
        """
        # Check if opportunity exists
        opportunity = db.query(Opportunity).filter(
            Opportunity.opportunity_id == opportunity_id
        ).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Check if already saved
        existing = db.query(SavedOpportunity).filter(
            and_(
                SavedOpportunity.user_id == user_id,
                SavedOpportunity.opportunity_id == opportunity_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opportunity already saved"
            )
        
        # Create saved opportunity
        saved_opp = SavedOpportunity(
            user_id=user_id,
            opportunity_id=opportunity_id,
            saved_at=datetime.utcnow()
        )
        
        db.add(saved_opp)
        db.commit()
        db.refresh(saved_opp)
        
        return saved_opp
    
    def unsave_opportunity(
        self,
        user_id: int,
        opportunity_id: int,
        db: Session
    ):
        """
        Remove saved opportunity
        """
        saved_opp = db.query(SavedOpportunity).filter(
            and_(
                SavedOpportunity.user_id == user_id,
                SavedOpportunity.opportunity_id == opportunity_id
            )
        ).first()
        
        if not saved_opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved opportunity not found"
            )
        
        db.delete(saved_opp)
        db.commit()
    
    def get_saved_opportunities(
        self,
        user_id: int,
        db: Session
    ) -> List[Opportunity]:
        """
        Get all saved opportunities for a user
        """
        saved = db.query(SavedOpportunity).filter(
            SavedOpportunity.user_id == user_id
        ).order_by(desc(SavedOpportunity.saved_at)).all()
        
        opportunities = [s.opportunity for s in saved]
        
        # Mark all as saved
        for opp in opportunities:
            opp.is_saved = True
        
        return opportunities
    
    def create_opportunity(
        self,
        opportunity_data: OpportunityCreate,
        db: Session
    ) -> Opportunity:
        """
        Create a new opportunity (used by scraper or admin)
        """
        # Create opportunity
        opportunity = Opportunity(
            title=opportunity_data.title,
            description=opportunity_data.description,
            link=opportunity_data.link,
            source=opportunity_data.source,
            location=opportunity_data.location,
            deadline=opportunity_data.deadline
        )
        
        db.add(opportunity)
        db.flush()
        
        # Add required skills
        if opportunity_data.required_skills:
            for skill_name in opportunity_data.required_skills:
                # Get or create skill
                skill = db.query(Skill).filter(
                    Skill.skill_name == skill_name
                ).first()
                
                if not skill:
                    skill = Skill(skill_name=skill_name)
                    db.add(skill)
                    db.flush()
                
                # Link skill to opportunity
                opp_skill = OpportunitySkill(
                    opportunity_id=opportunity.opportunity_id,
                    skill_id=skill.skill_id
                )
                db.add(opp_skill)
        
        db.commit()
        db.refresh(opportunity)
        
        return opportunity
    
    def get_opportunity_skills(
        self,
        opportunity_id: int,
        db: Session
    ) -> List[str]:
        """
        Get all skills for an opportunity
        """
        opp_skills = db.query(OpportunitySkill).filter(
            OpportunitySkill.opportunity_id == opportunity_id
        ).all()
        
        skills = []
        for os in opp_skills:
            skill = db.query(Skill).filter(
                Skill.skill_id == os.skill_id
            ).first()
            if skill:
                skills.append(skill.skill_name)
        
        return skills
    
    def delete_old_opportunities(
        self,
        days_old: int,
        db: Session
    ):
        """
        Delete opportunities older than specified days
        Used for cleanup
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted = db.query(Opportunity).filter(
            Opportunity.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return deleted

# Initialize service
opportunity_service = OpportunityService()
