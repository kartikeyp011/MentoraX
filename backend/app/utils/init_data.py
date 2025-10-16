"""
Initialize database with sample data for testing
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.opportunity_service import opportunity_service
from app.services.resource_service import resource_service
from app.services.scraper_service import scraper_service
from app.models.skill import Skill
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_sample_data():
    """Initialize database with sample data"""
    db = SessionLocal()
    
    try:
        logger.info("Starting data initialization...")
        
        # 1. Create sample skills
        logger.info("Creating sample skills...")
        sample_skills = [
            {"skill_name": "Python", "description": "Programming language"},
            {"skill_name": "JavaScript", "description": "Web programming language"},
            {"skill_name": "React", "description": "Frontend framework"},
            {"skill_name": "Node.js", "description": "Backend runtime"},
            {"skill_name": "Machine Learning", "description": "AI and ML techniques"},
            {"skill_name": "SQL", "description": "Database query language"},
            {"skill_name": "Docker", "description": "Containerization platform"},
            {"skill_name": "AWS", "description": "Cloud computing platform"},
            {"skill_name": "Git", "description": "Version control system"},
            {"skill_name": "Data Science", "description": "Data analysis and statistics"},
        ]
        
        skill_count = 0
        for skill_data in sample_skills:
            existing = db.query(Skill).filter(
                Skill.skill_name == skill_data["skill_name"]
            ).first()
            
            if not existing:
                skill = Skill(**skill_data)
                db.add(skill)
                skill_count += 1
        
        db.commit()
        logger.info(f"Created {skill_count} skills")
        
        # 2. Create sample opportunities
        logger.info("Creating sample opportunities...")
        opp_count = await scraper_service._create_sample_opportunities(db)
        logger.info(f"Created {opp_count} opportunities")
        
        # 3. Create sample resources
        logger.info("Creating sample resources...")
        resource_count = resource_service.create_sample_resources(db)
        logger.info(f"Created {resource_count} resources")
        
        # 4. Build FAISS index
        logger.info("Building FAISS index...")
        resource_service.rebuild_faiss_index(db)
        logger.info("FAISS index built successfully")
        
        logger.info("✅ Data initialization complete!")
        
        return {
            "skills": skill_count,
            "opportunities": opp_count,
            "resources": resource_count
        }
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_sample_data())
