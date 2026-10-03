from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from services.ai_core.search.search_base import SearchCategory, GroundedSearchResponse
from services.ai_core.search.search_pipeline import get_search_pipeline, SearchPipeline

router = APIRouter(prefix="/search", tags=["Grounded AI Search"])

class SearchQueryRequest(BaseModel):
    query: str
    category: Optional[SearchCategory] = SearchCategory.WEB
    max_results: Optional[int] = 5

@router.post("/query", response_model=GroundedSearchResponse)
async def execute_search(
    payload: SearchQueryRequest,
    pipeline: SearchPipeline = Depends(get_search_pipeline)
):
    return await pipeline.execute(
        query=payload.query,
        category=payload.category or SearchCategory.WEB,
        max_results=payload.max_results or 5
    )

@router.get("/categories")
async def list_categories():
    return [c.value for c in SearchCategory]
