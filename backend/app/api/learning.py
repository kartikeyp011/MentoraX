from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.resource import (
    ResourceResponse,
    ResourceSearchRequest,
    ResourceSearchResponse,
    ResourceCreate
)
from app.services.resource_service import resource_service
from app.services.user_service import user_service
from app.services.faiss_service import faiss_service

router = APIRouter(prefix="/resources", tags=["Learning Zone"])

@router.post("/search", response_model=ResourceSearchResponse)
async def search_resources(
    search_request: ResourceSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search learning resources using semantic search (FAISS)
    Can filter by skills and resource type
    """
    results = resource_service.search_resources(search_request, db)
    
    # Format response
    resources = [ResourceResponse(**r) for r in results]
    
    return ResourceSearchResponse(
        resources=resources,
        total=len(resources),
        query=search_request.query
    )

@router.get("/all", response_model=List[ResourceResponse])
async def get_all_resources(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all learning resources with pagination
    """
    resources, total = resource_service.get_all_resources(limit, offset, db)
    
    results = []
    for resource in resources:
        skills = resource_service.get_resource_skills(resource.resource_id, db)
        results.append(ResourceResponse(
            resource_id=resource.resource_id,
            title=resource.title,
            description=resource.description,
            url=resource.url,
            resource_type=resource.resource_type,
            related_skills=skills,
            created_at=resource.created_at,
            updated_at=resource.updated_at
        ))
    
    return results

@router.get("/recommended", response_model=List[ResourceResponse])
async def get_recommended_resources(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized resource recommendations
    Based on user skills and career goals
    """
    # Get user skills
    user_skills_data = user_service.get_user_skills(current_user.user_id, db)
    user_skills = [s['skill_name'] for s in user_skills_data]
    
    # Get recommendations
    results = resource_service.get_recommended_resources_for_user(
        user_skills=user_skills,
        career_goal=current_user.career_goal,
        db=db,
        limit=limit
    )
    
    return [ResourceResponse(**r) for r in results]

@router.post("/create", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new learning resource
    For admin/testing purposes
    """
    resource = resource_service.create_resource(resource_data, db)
    skills = resource_service.get_resource_skills(resource.resource_id, db)
    
    return ResourceResponse(
        resource_id=resource.resource_id,
        title=resource.title,
        description=resource.description,
        url=resource.url,
        resource_type=resource.resource_type,
        related_skills=skills,
        created_at=resource.created_at,
        updated_at=resource.updated_at
    )

@router.post("/populate-samples")
async def populate_sample_resources(
    db: Session = Depends(get_db)
):
    """
    Create sample learning resources for testing
    """
    count = resource_service.create_sample_resources(db)
    
    return {
        "success": True,
        "message": f"Created {count} sample resources"
    }

@router.post("/rebuild-index")
async def rebuild_faiss_index(
    db: Session = Depends(get_db)
):
    """
    Rebuild FAISS index from database
    Use this after bulk updates or data changes
    """
    resource_service.rebuild_faiss_index(db)
    
    stats = faiss_service.get_index_stats()
    
    return {
        "success": True,
        "message": "FAISS index rebuilt successfully",
        "stats": stats
    }

@router.get("/index-stats")
async def get_index_stats():
    """
    Get FAISS index statistics
    """
    return faiss_service.get_index_stats()
