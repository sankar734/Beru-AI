import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from apps.api.database import get_db, DatabaseManager
from apps.api.auth import get_current_user
from apps.api.models.memory import (
    MemoryType,
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    KnowledgeEntity,
    KnowledgeRelation,
)
from services.ai_core.rag.vector_store import get_vector_store, VectorRecord
from services.ai_core.registry import get_provider_registry

router = APIRouter(prefix="/memory", tags=["Controlled Memory & Knowledge Graph"])

@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    mem_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": mem_id,
        "user_id": current_user["id"],
        "content": payload.content,
        "memory_type": payload.memory_type.value,
        "project_id": payload.project_id,
        "is_active": True,
        "tags": payload.tags or [],
        "created_at": now_str,
        "updated_at": now_str,
    }

    # Generate embedding for memory retrieval
    provider = get_provider_registry().get_provider("mock")
    embs = await provider.generate_embeddings([payload.content])
    if embs:
        await get_vector_store().upsert("nova_memories", [
            VectorRecord(
                id=mem_id,
                vector=embs[0],
                payload={
                    "memory_id": mem_id,
                    "user_id": current_user["id"],
                    "project_id": payload.project_id,
                    "content": payload.content,
                    "memory_type": payload.memory_type.value,
                }
            )
        ])

    col = db.get_collection("memories")
    await col.insert_one(doc)
    return MemoryResponse(**doc)

@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    memory_type: Optional[MemoryType] = None,
    project_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("memories")
    query = {"user_id": current_user["id"]}
    if memory_type:
        query["memory_type"] = memory_type.value
    if project_id:
        query["project_id"] = project_id
    if is_active is not None:
        query["is_active"] = is_active

    docs = await col.find(query)
    docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [MemoryResponse(**d) for d in docs]

@router.patch("/{id}", response_model=MemoryResponse)
async def update_memory(
    id: str,
    payload: MemoryUpdate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("memories")
    doc = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Memory not found")

    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if payload.content is not None:
        update_fields["content"] = payload.content
    if payload.memory_type is not None:
        update_fields["memory_type"] = payload.memory_type.value
    if payload.is_active is not None:
        update_fields["is_active"] = payload.is_active
    if payload.tags is not None:
        update_fields["tags"] = payload.tags

    await col.update_one({"id": id}, {"$set": update_fields})
    updated = await col.find_one({"id": id})
    return MemoryResponse(**updated)

@router.delete("/{id}")
async def delete_memory(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("memories")
    doc = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Memory not found")

    await col.delete_one({"id": id})
    await get_vector_store().delete_by_file_id("nova_memories", id)
    return {"message": "Memory deleted successfully", "id": id}

@router.delete("")
async def clear_all_memories(
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("memories")
    docs = await col.find({"user_id": current_user["id"]})
    for d in docs:
        await col.delete_one({"id": d["id"]})
    return {"message": "All memories cleared successfully", "count": len(docs)}

@router.post("/graph/relations", response_model=KnowledgeRelation)
async def create_graph_relation(
    relation: KnowledgeRelation,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("knowledge_relations")
    doc = relation.model_dump()
    doc["user_id"] = current_user["id"]
    await col.insert_one(doc)
    return relation
