from app.database import Base
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.opportunity import Opportunity, OpportunitySkill, SavedOpportunity
from app.models.resource import Resource, ResourceSkill
from app.models.resume import Resume

# Import all models here for Alembic to detect them
__all__ = [
    "Base",
    "User",
    "Skill",
    "UserSkill",
    "Opportunity",
    "OpportunitySkill",
    "SavedOpportunity",
    "Resource",
    "ResourceSkill",
    "Resume"
]
