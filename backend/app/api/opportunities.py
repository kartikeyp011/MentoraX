from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.opportunity import (
    OpportunityResponse,
    OpportunityFilterRequest,
    OpportunitiesListResponse,
    SaveOpportunityRequest,
    SaveOpportunityResponse,
    OpportunityCreate
)
from app.services.opportunity_service import opportunity_service
from app.services.scraper_service import scraper_service

router = APIRouter(prefix="/opportunities", tags=["Opportunities Hub"])

@router.get("/all", response_model=OpportunitiesListResponse)
async def get_all_opportunities(
    limit: int = 50,
    offset: int = 0,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get all opportunities with pagination
    Authentication optional - saved status shown if authenticated
    """
    user_id = current_user.user_id if current_user else None
    
    opportunities, total = opportunity_service.get_all_opportunities(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db=db
    )
    
    # Format response
    opp_list = []
    for opp in opportunities:
        skills = opportunity_service.get_opportunity_skills(opp.opportunity_id, db)
        opp_list.append(OpportunityResponse(
            opportunity_id=opp.opportunity_id,
            title=opp.title,
            description=opp.description,
            link=opp.link,
            source=opp.source,
            location=opp.location,
            deadline=opp.deadline,
            required_skills=skills,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
            is_saved=getattr(opp, 'is_saved', False)
        ))
    
    return OpportunitiesListResponse(
        opportunities=opp_list,
        total=total,
        limit=limit,
        offset=offset
    )

@router.post("/filter", response_model=OpportunitiesListResponse)
async def filter_opportunities(
    filter_request: OpportunityFilterRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Filter opportunities by skills, location, source, etc.
    Authentication optional
    """
    user_id = current_user.user_id if current_user else None
    
    opportunities, total = opportunity_service.filter_opportunities(
        filter_request=filter_request,
        user_id=user_id,
        db=db
    )
    
    # Format response
    opp_list = []
    for opp in opportunities:
        skills = opportunity_service.get_opportunity_skills(opp.opportunity_id, db)
        opp_list.append(OpportunityResponse(
            opportunity_id=opp.opportunity_id,
            title=opp.title,
            description=opp.description,
            link=opp.link,
            source=opp.source,
            location=opp.location,
            deadline=opp.deadline,
            required_skills=skills,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
            is_saved=getattr(opp, 'is_saved', False)
        ))
    
    return OpportunitiesListResponse(
        opportunities=opp_list,
        total=total,
        limit=filter_request.limit,
        offset=filter_request.offset
    )

@router.post("/save", response_model=SaveOpportunityResponse)
async def save_opportunity(
    request: SaveOpportunityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save/bookmark an opportunity
    Requires authentication
    """
    saved_opp = opportunity_service.save_opportunity(
        user_id=current_user.user_id,
        opportunity_id=request.opportunity_id,
        db=db
    )
    
    return SaveOpportunityResponse(
        success=True,
        message="Opportunity saved successfully",
        opportunity_id=saved_opp.opportunity_id
    )

@router.delete("/save/{opportunity_id}")
async def unsave_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove saved opportunity
    Requires authentication
    """
    opportunity_service.unsave_opportunity(
        user_id=current_user.user_id,
        opportunity_id=opportunity_id,
        db=db
    )
    
    return {
        "success": True,
        "message": "Opportunity removed from saved list"
    }

@router.get("/saved", response_model=List[OpportunityResponse])
async def get_saved_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved opportunities for current user
    Requires authentication
    """
    opportunities = opportunity_service.get_saved_opportunities(
        user_id=current_user.user_id,
        db=db
    )
    
    # Format response
    opp_list = []
    for opp in opportunities:
        skills = opportunity_service.get_opportunity_skills(opp.opportunity_id, db)
        opp_list.append(OpportunityResponse(
            opportunity_id=opp.opportunity_id,
            title=opp.title,
            description=opp.description,
            link=opp.link,
            source=opp.source,
            location=opp.location,
            deadline=opp.deadline,
            required_skills=skills,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
            is_saved=True
        ))
    
    return opp_list

@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger opportunity scraping
    This should be called by a cron job or admin
    For MVP: Can be called manually
    """
    # Run scraping in background
    background_tasks.add_task(scraper_service.scrape_all_sources, db)
    
    return {
        "success": True,
        "message": "Scraping started in background"
    }

@router.post("/create", response_model=OpportunityResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new opportunity manually
    For admin/testing purposes
    """
    opportunity = opportunity_service.create_opportunity(
        opportunity_data=opportunity_data,
        db=db
    )
    
    skills = opportunity_service.get_opportunity_skills(opportunity.opportunity_id, db)
    
    return OpportunityResponse(
        opportunity_id=opportunity.opportunity_id,
        title=opportunity.title,
        description=opportunity.description,
        link=opportunity.link,
        source=opportunity.source,
        location=opportunity.location,
        deadline=opportunity.deadline,
        required_skills=skills,
        created_at=opportunity.created_at,
        updated_at=opportunity.updated_at,
        is_saved=False
    )
