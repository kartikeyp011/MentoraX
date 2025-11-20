from fastapi import APIRouter, HTTPException
from backend.models import ResourceSearch
from backend.database import fetch_all
from backend.faiss_utils import search_faiss

router = APIRouter(prefix="/resources", tags=["Learning Resources"])


@router.post("/search")
async def search_resources(search: ResourceSearch):
    """Search learning resources using FAISS semantic search"""
    try:
        # Use FAISS to find relevant resources
        results = search_faiss(search.query, index_type='resources', top_k=10)

        # Format results
        resources = []
        for result in results:
            resources.append({
                'resource_id': result['id'],
                'title': result['title'],
                'description': result['description'],
                'url': result['url'],
                'relevance_score': 1.0 / (1.0 + result['distance'])  # Convert distance to score
            })

        return {
            "success": True,
            "query": search.query,
            "resources": resources,
            "count": len(resources)
        }

    except Exception as e:
        print(f"Error searching resources: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching resources: {str(e)}")


@router.get("/all")
async def get_all_resources():
    """Get all resources"""
    try:
        resources = fetch_all("SELECT * FROM resources ORDER BY created_at DESC")

        return {
            "success": True,
            "resources": resources,
            "count": len(resources)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {str(e)}")