import uuid
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel

from apps.api.database import get_db, DatabaseManager
from apps.api.auth import get_current_user
from services.ai_core.research.research_engine import (
    get_research_engine,
    DeepResearchEngine,
    ResearchJobState,
    SubQuestion,
    EvidenceItem
)

router = APIRouter(prefix="/research", tags=["Deep Research"])

class CreateResearchJobRequest(BaseModel):
    goal: str
    depth: Optional[str] = "comprehensive"  # quick, standard, comprehensive

@router.post("/jobs", response_model=ResearchJobState, status_code=status.HTTP_201_CREATED)
async def create_research_job(
    payload: CreateResearchJobRequest,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
    engine: DeepResearchEngine = Depends(get_research_engine)
):
    job_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": job_id,
        "user_id": current_user["id"],
        "goal": payload.goal,
        "status": "QUEUED",
        "progress": 5,
        "subquestions": [],
        "evidence": [],
        "sources": [],
        "final_report": None,
        "created_at": now_str,
        "updated_at": now_str,
    }

    jobs_col = db.get_collection("research_jobs")
    await jobs_col.insert_one(doc)

    # Execute research job immediately
    completed_state = await engine.execute_job(job_id, payload.goal, current_user["id"], db)
    return completed_state

@router.get("/jobs", response_model=List[ResearchJobState])
async def list_research_jobs(
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    jobs_col = db.get_collection("research_jobs")
    docs = await jobs_col.find({"user_id": current_user["id"]})
    docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [ResearchJobState(**d) for d in docs]

@router.get("/jobs/{id}", response_model=ResearchJobState)
async def get_research_job(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    jobs_col = db.get_collection("research_jobs")
    doc = await jobs_col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Research job not found")
    return ResearchJobState(**doc)

@router.post("/jobs/{id}/cancel", response_model=ResearchJobState)
async def cancel_research_job(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    jobs_col = db.get_collection("research_jobs")
    doc = await jobs_col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Research job not found")

    await jobs_col.update_one(
        {"id": id},
        {"$set": {"status": "CANCELLED", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    updated = await jobs_col.find_one({"id": id})
    return ResearchJobState(**updated)
