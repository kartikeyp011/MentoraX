from fastapi import APIRouter, HTTPException, Header
from .models import OpportunityFilter
from .database import fetch_all, execute_query
from .auth import verify_session

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("/all")
async def get_all_opportunities():
    """Get all opportunities"""
    try:
        query = """
                SELECT o.*, GROUP_CONCAT(s.skill_name) as required_skills
                FROM opportunities o
                         LEFT JOIN opportunity_skills os ON o.opportunity_id = os.opportunity_id
                         LEFT JOIN skills s ON os.skill_id = s.skill_id
                GROUP BY o.opportunity_id
                ORDER BY o.deadline ASC \
                """
        opportunities = fetch_all(query)

        # Format the results
        for opp in opportunities:
            if opp['required_skills']:
                opp['required_skills'] = opp['required_skills'].split(',')
            else:
                opp['required_skills'] = []

        return {"success": True, "opportunities": opportunities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching opportunities: {str(e)}")


@router.post("/filter")
async def filter_opportunities(filters: OpportunityFilter):
    """Filter opportunities by skills, location, deadline"""
    try:
        query = """
                SELECT DISTINCT o.*, GROUP_CONCAT(DISTINCT s.skill_name) as required_skills
                FROM opportunities o
                         LEFT JOIN opportunity_skills os ON o.opportunity_id = os.opportunity_id
                         LEFT JOIN skills s ON os.skill_id = s.skill_id
                WHERE 1 = 1 \
                """
        params = []

        # Filter by skills
        if filters.skill_ids and len(filters.skill_ids) > 0:
            placeholders = ','.join(['%s'] * len(filters.skill_ids))
            query += f" AND o.opportunity_id IN (SELECT opportunity_id FROM opportunity_skills WHERE skill_id IN ({placeholders}))"
            params.extend(filters.skill_ids)

        # Filter by location
        if filters.location:
            query += " AND o.location LIKE %s"
            params.append(f"%{filters.location}%")

        # Filter by deadline
        if filters.deadline_after:
            query += " AND o.deadline >= %s"
            params.append(filters.deadline_after)

        query += " GROUP BY o.opportunity_id ORDER BY o.deadline ASC"

        opportunities = fetch_all(query, tuple(params))

        # Format results
        for opp in opportunities:
            if opp['required_skills']:
                opp['required_skills'] = opp['required_skills'].split(',')
            else:
                opp['required_skills'] = []

        return {"success": True, "opportunities": opportunities, "count": len(opportunities)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering opportunities: {str(e)}")


@router.post("/save/{opportunity_id}")
async def save_opportunity(opportunity_id: int, authorization: str = Header(None)):
    """Save/bookmark an opportunity (placeholder for future implementation)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    # TODO: Implement saved_opportunities table and logic
    return {"success": True, "message": "Opportunity saved (feature coming soon)"}


@router.get("/stats")
async def get_opportunities_stats():
    """Get statistics about opportunities"""
    try:
        total = fetch_all("SELECT COUNT(*) as count FROM opportunities")[0]['count']
        by_source = fetch_all("SELECT source, COUNT(*) as count FROM opportunities GROUP BY source")
        by_location = fetch_all(
            "SELECT location, COUNT(*) as count FROM opportunities GROUP BY location ORDER BY count DESC LIMIT 5")

        return {
            "success": True,
            "stats": {
                "total": total,
                "by_source": by_source,
                "by_location": by_location
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")