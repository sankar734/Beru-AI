import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from apps.api.database import get_db, DatabaseManager
from apps.api.auth import get_current_user
from apps.api.models.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects & Context Spaces"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("projects")
    proj_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": proj_id,
        "user_id": current_user["id"],
        "name": payload.name,
        "description": payload.description or "",
        "system_instructions": payload.system_instructions or "",
        "custom_rules": payload.custom_rules or [],
        "created_at": now_str,
        "updated_at": now_str,
    }

    await col.insert_one(doc)
    return ProjectResponse(**doc, file_count=0, artifact_count=0, task_count=0)

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("projects")
    files_col = db.get_collection("files")
    docs = await col.find({"user_id": current_user["id"]})

    results = []
    for d in docs:
        file_cnt = len(await files_col.find({"project_id": d["id"]}))
        results.append(ProjectResponse(**d, file_count=file_cnt, artifact_count=0, task_count=0))
    return results

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("projects")
    files_col = db.get_collection("files")
    doc = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")

    file_cnt = len(await files_col.find({"project_id": id}))
    return ProjectResponse(**doc, file_count=file_cnt, artifact_count=0, task_count=0)

@router.patch("/{id}", response_model=ProjectResponse)
async def update_project(
    id: str,
    payload: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("projects")
    doc = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")

    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if payload.name is not None:
        update_fields["name"] = payload.name
    if payload.description is not None:
        update_fields["description"] = payload.description
    if payload.system_instructions is not None:
        update_fields["system_instructions"] = payload.system_instructions
    if payload.custom_rules is not None:
        update_fields["custom_rules"] = payload.custom_rules

    await col.update_one({"id": id}, {"$set": update_fields})
    updated = await col.find_one({"id": id})
    return ProjectResponse(**updated, file_count=0, artifact_count=0, task_count=0)

@router.delete("/{id}")
async def delete_project(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("projects")
    doc = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")

    await col.delete_one({"id": id})
    return {"message": "Project deleted successfully", "id": id}
