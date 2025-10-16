from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.models.resource import Resource, ResourceSkill
from app.models.skill import Skill
from app.schemas.resource import ResourceCreate, ResourceSearchRequest
from app.services.faiss_service import faiss_service
import logging

logger = logging.getLogger(__name__)

class ResourceService:
    """Service for learning resource management"""
    
    def get_all_resources(
        self,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> tuple[List[Resource], int]:
        """Get all resources with pagination"""
        query = db.query(Resource).order_by(Resource.created_at.desc())
        
        total = query.count()
        resources = query.limit(limit).offset(offset).all()
        
        return resources, total
    
    def search_resources(
        self,
        search_request: ResourceSearchRequest,
        db: Session
    ) -> List[Dict]:
        """
        Search resources using FAISS semantic search
        Combined with SQL filtering
        """
        # First, use FAISS for semantic search
        faiss_results = faiss_service.search_similar_resources(
            query=search_request.query,
            k=search_request.limit * 2  # Get more results for filtering
        )
        
        if not faiss_results:
            # Fallback to SQL search if FAISS has no results
            return self._sql_search(search_request, db)
        
        # Get resource IDs from FAISS results
        resource_ids = [r['resource_id'] for r in faiss_results]
        
        # Query database for these resources
        query = db.query(Resource).filter(Resource.resource_id.in_(resource_ids))
        
        # Apply filters
        if search_request.skill_filter:
            skill_ids = db.query(Skill.skill_id).filter(
                Skill.skill_name.in_(search_request.skill_filter)
            ).all()
            skill_ids = [s[0] for s in skill_ids]
            
            if skill_ids:
                query = query.join(ResourceSkill).filter(
                    ResourceSkill.skill_id.in_(skill_ids)
                )
        
        if search_request.resource_type:
            query = query.filter(Resource.resource_type == search_request.resource_type)
        
        resources = query.limit(search_request.limit).all()
        
        # Format results with similarity scores
        results = []
        faiss_scores = {r['resource_id']: r['similarity_score'] for r in faiss_results}
        
        for resource in resources:
            skills = self.get_resource_skills(resource.resource_id, db)
            results.append({
                'resource_id': resource.resource_id,
                'title': resource.title,
                'description': resource.description,
                'url': resource.url,
                'resource_type': resource.resource_type,
                'related_skills': skills,
                'similarity_score': faiss_scores.get(resource.resource_id, 0),
                'created_at': resource.created_at,
                'updated_at': resource.updated_at
            })
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results
    
    def _sql_search(
        self,
        search_request: ResourceSearchRequest,
        db: Session
    ) -> List[Dict]:
        """Fallback SQL-based search"""
        query = db.query(Resource)
        
        # Text search
        search_term = f"%{search_request.query}%"
        query = query.filter(
            or_(
                Resource.title.ilike(search_term),
                Resource.description.ilike(search_term)
            )
        )
        
        # Apply filters
        if search_request.skill_filter:
            skill_ids = db.query(Skill.skill_id).filter(
                Skill.skill_name.in_(search_request.skill_filter)
            ).all()
            skill_ids = [s[0] for s in skill_ids]
            
            if skill_ids:
                query = query.join(ResourceSkill).filter(
                    ResourceSkill.skill_id.in_(skill_ids)
                )
        
        if search_request.resource_type:
            query = query.filter(Resource.resource_type == search_request.resource_type)
        
        resources = query.limit(search_request.limit).all()
        
        results = []
        for resource in resources:
            skills = self.get_resource_skills(resource.resource_id, db)
            results.append({
                'resource_id': resource.resource_id,
                'title': resource.title,
                'description': resource.description,
                'url': resource.url,
                'resource_type': resource.resource_type,
                'related_skills': skills,
                'similarity_score': 0.5,  # Default score
                'created_at': resource.created_at,
                'updated_at': resource.updated_at
            })
        
        return results
    
    def create_resource(
        self,
        resource_data: ResourceCreate,
        db: Session
    ) -> Resource:
        """Create a new learning resource"""
        # Create resource
        resource = Resource(
            title=resource_data.title,
            description=resource_data.description,
            url=resource_data.url,
            resource_type=resource_data.resource_type
        )
        
        db.add(resource)
        db.flush()
        
        # Add related skills
        if resource_data.related_skills:
            for skill_name in resource_data.related_skills:
                # Get or create skill
                skill = db.query(Skill).filter(
                    Skill.skill_name == skill_name
                ).first()
                
                if not skill:
                    skill = Skill(skill_name=skill_name)
                    db.add(skill)
                    db.flush()
                
                # Link skill to resource
                resource_skill = ResourceSkill(
                    resource_id=resource.resource_id,
                    skill_id=skill.skill_id
                )
                db.add(resource_skill)
        
        db.commit()
        db.refresh(resource)
        
        # Add to FAISS index
        self._add_resource_to_faiss(resource, db)
        
        return resource
    
    def _add_resource_to_faiss(self, resource: Resource, db: Session):
        """Add single resource to FAISS index"""
        try:
            skills = self.get_resource_skills(resource.resource_id, db)
            faiss_data = [{
                'resource_id': resource.resource_id,
                'title': resource.title,
                'description': resource.description or '',
                'resource_type': resource.resource_type,
                'related_skills': skills
            }]
            faiss_service.add_resources(faiss_data)
        except Exception as e:
            logger.error(f"Failed to add resource to FAISS: {str(e)}")
    
    def get_resource_skills(
        self,
        resource_id: int,
        db: Session
    ) -> List[str]:
        """Get all skills for a resource"""
        resource_skills = db.query(ResourceSkill).filter(
            ResourceSkill.resource_id == resource_id
        ).all()
        
        skills = []
        for rs in resource_skills:
            skill = db.query(Skill).filter(
                Skill.skill_id == rs.skill_id
            ).first()
            if skill:
                skills.append(skill.skill_name)
        
        return skills
    
    def get_recommended_resources_for_user(
        self,
        user_skills: List[str],
        career_goal: Optional[str],
        db: Session,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recommended resources based on user profile
        Uses skill gaps and career goals
        """
        # Build query based on skills and career goal
        query_parts = user_skills.copy()
        if career_goal:
            query_parts.append(career_goal)
        
        query_text = " ".join(query_parts)
        
        # Search using FAISS
        results = faiss_service.search_similar_resources(query_text, k=limit)
        
        if not results:
            return []
        
        # Enrich with database data
        resource_ids = [r['resource_id'] for r in results]
        resources = db.query(Resource).filter(
            Resource.resource_id.in_(resource_ids)
        ).all()
        
        enriched_results = []
        scores = {r['resource_id']: r['similarity_score'] for r in results}
        
        for resource in resources:
            skills = self.get_resource_skills(resource.resource_id, db)
            enriched_results.append({
                'resource_id': resource.resource_id,
                'title': resource.title,
                'description': resource.description,
                'url': resource.url,
                'resource_type': resource.resource_type,
                'related_skills': skills,
                'similarity_score': scores.get(resource.resource_id, 0),
                'created_at': resource.created_at
            })
        
        # Sort by similarity
        enriched_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return enriched_results
    
    def rebuild_faiss_index(self, db: Session):
        """Rebuild FAISS index from all resources in database"""
        resources = db.query(Resource).all()
        
        faiss_data = []
        for resource in resources:
            skills = self.get_resource_skills(resource.resource_id, db)
            faiss_data.append({
                'resource_id': resource.resource_id,
                'title': resource.title,
                'description': resource.description or '',
                'resource_type': resource.resource_type,
                'related_skills': skills
            })
        
        faiss_service.rebuild_resource_index(faiss_data)
        logger.info(f"Rebuilt FAISS index with {len(faiss_data)} resources")
    
    def create_sample_resources(self, db: Session) -> int:
        """Create sample learning resources for testing"""
        sample_resources = [
            {
                "title": "Python for Beginners - Complete Course",
                "description": "Learn Python programming from scratch. Covers basics, data structures, OOP, and more.",
                "url": "https://www.coursera.org/learn/python",
                "resource_type": "course",
                "related_skills": ["Python", "Programming"]
            },
            {
                "title": "JavaScript & React - The Complete Guide",
                "description": "Master JavaScript and React.js. Build modern web applications with hooks and Redux.",
                "url": "https://www.udemy.com/course/react-complete-guide",
                "resource_type": "course",
                "related_skills": ["JavaScript", "React", "Web Development"]
            },
            {
                "title": "Machine Learning Specialization",
                "description": "Deep dive into ML algorithms, neural networks, and practical applications.",
                "url": "https://www.coursera.org/specializations/machine-learning",
                "resource_type": "course",
                "related_skills": ["Machine Learning", "Python", "Data Science"]
            },
            {
                "title": "SQL for Data Analysis",
                "description": "Learn SQL queries, joins, aggregations, and database optimization.",
                "url": "https://mode.com/sql-tutorial",
                "resource_type": "tutorial",
                "related_skills": ["SQL", "Data Analysis", "Databases"]
            },
            {
                "title": "Docker & Kubernetes for Developers",
                "description": "Containerization and orchestration for modern applications.",
                "url": "https://www.udemy.com/course/docker-kubernetes",
                "resource_type": "course",
                "related_skills": ["Docker", "Kubernetes", "DevOps"]
            },
            {
                "title": "AWS Certified Solutions Architect",
                "description": "Prepare for AWS certification. Learn cloud architecture and best practices.",
                "url": "https://aws.amazon.com/certification",
                "resource_type": "certification",
                "related_skills": ["AWS", "Cloud Computing", "Architecture"]
            },
            {
                "title": "Git and GitHub Essentials",
                "description": "Version control fundamentals, branching strategies, and collaboration.",
                "url": "https://www.freecodecamp.org/news/git-and-github-for-beginners",
                "resource_type": "article",
                "related_skills": ["Git", "GitHub", "Version Control"]
            },
            {
                "title": "Data Structures and Algorithms",
                "description": "Essential DSA concepts for coding interviews and competitive programming.",
                "url": "https://www.geeksforgeeks.org/data-structures",
                "resource_type": "tutorial",
                "related_skills": ["Data Structures", "Algorithms", "Problem Solving"]
            },
            {
                "title": "Full Stack Web Development Bootcamp",
                "description": "End-to-end web development: HTML, CSS, JavaScript, Node.js, MongoDB.",
                "url": "https://www.theodinproject.com",
                "resource_type": "course",
                "related_skills": ["HTML", "CSS", "JavaScript", "Node.js", "MongoDB"]
            },
            {
                "title": "Cybersecurity Fundamentals",
                "description": "Introduction to security principles, encryption, and threat detection.",
                "url": "https://www.cybrary.it/course/introduction-to-it-and-cybersecurity",
                "resource_type": "course",
                "related_skills": ["Cybersecurity", "Network Security", "Ethical Hacking"]
            }
        ]
        
        count = 0
        for resource_data in sample_resources:
            try:
                # Check if exists
                existing = db.query(Resource).filter(
                    Resource.title == resource_data['title']
                ).first()
                
                if not existing:
                    resource_create = ResourceCreate(**resource_data)
                    self.create_resource(resource_create, db)
                    count += 1
            except Exception as e:
                logger.error(f"Failed to create resource: {str(e)}")
        
        return count

# Initialize service
resource_service = ResourceService()
