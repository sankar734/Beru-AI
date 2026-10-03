import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from apps.api.database import get_db, DatabaseManager
from apps.api.auth import get_current_user
from apps.api.models.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageCreate,
    MessageResponse,
    CitationModel,
    AttachmentModel,
)

router = APIRouter(prefix="/chat", tags=["Universal Chat"])

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    conv_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()
    
    doc = {
        "id": conv_id,
        "user_id": current_user["id"],
        "title": payload.title or "New Conversation",
        "mode": payload.mode or "AUTO",
        "project_id": payload.project_id,
        "pinned": False,
        "archived": False,
        "created_at": now_str,
        "updated_at": now_str,
    }
    await col.insert_one(doc)
    return ConversationResponse(**doc, message_count=0)

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    search: Optional[str] = None,
    pinned: Optional[bool] = None,
    archived: Optional[bool] = False,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    messages_col = db.get_collection("messages")
    query = {"user_id": current_user["id"]}
    if pinned is not None:
        query["pinned"] = pinned
    if archived is not None:
        query["archived"] = archived

    docs = await col.find(query)
    
    if search:
        s_lower = search.lower()
        docs = [d for d in docs if s_lower in d.get("title", "").lower()]

    docs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    results = []
    for d in docs:
        msg_count = len(await messages_col.find({"conversation_id": d["id"]}))
        results.append(ConversationResponse(**d, message_count=msg_count))
    return results

@router.get("/conversations/{id}", response_model=ConversationDetailResponse)
async def get_conversation(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    messages_col = db.get_collection("messages")

    conv = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    raw_msgs = await messages_col.find({"conversation_id": id})
    raw_msgs.sort(key=lambda x: x.get("created_at", ""))
    
    messages = [MessageResponse(**m) for m in raw_msgs]
    return ConversationDetailResponse(**conv, message_count=len(messages), messages=messages)

@router.patch("/conversations/{id}", response_model=ConversationResponse)
async def update_conversation(
    id: str,
    payload: ConversationUpdate,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    conv = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if payload.title is not None:
        update_fields["title"] = payload.title
    if payload.mode is not None:
        update_fields["mode"] = payload.mode
    if payload.pinned is not None:
        update_fields["pinned"] = payload.pinned
    if payload.archived is not None:
        update_fields["archived"] = payload.archived

    await col.update_one({"id": id}, {"$set": update_fields})
    updated = await col.find_one({"id": id})
    return ConversationResponse(**updated)

@router.delete("/conversations/{id}")
async def delete_conversation(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    messages_col = db.get_collection("messages")

    conv = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await col.delete_one({"id": id})
    # Delete related messages
    msgs = await messages_col.find({"conversation_id": id})
    for m in msgs:
        await messages_col.delete_one({"id": m["id"]})

    return {"message": "Conversation deleted successfully", "id": id}

@router.post("/conversations/{id}/messages")
async def send_message(
    id: str,
    payload: MessageCreate,
    stream: bool = Query(default=False),
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    messages_col = db.get_collection("messages")

    conv = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now_str = datetime.now(timezone.utc).isoformat()
    
    # Auto-generate title if this is the first message
    existing_msgs = await messages_col.find({"conversation_id": id})
    if len(existing_msgs) == 0 and conv.get("title") in ["New Conversation", "Untitled"]:
        new_title = payload.content[:32].strip() + ("..." if len(payload.content) > 32 else "")
        await col.update_one({"id": id}, {"$set": {"title": new_title, "updated_at": now_str}})

    # 1. Save user message
    user_msg_id = str(uuid.uuid4())
    user_msg_doc = {
        "id": user_msg_id,
        "conversation_id": id,
        "role": "user",
        "content": payload.content,
        "mode": payload.mode or conv.get("mode", "AUTO"),
        "attachments": [a.model_dump() for a in payload.attachments] if payload.attachments else [],
        "created_at": now_str,
    }
    await messages_col.insert_one(user_msg_doc)

    # 2. Assistant response generation
    asst_msg_id = str(uuid.uuid4())
    asst_now_str = datetime.now(timezone.utc).isoformat()
    
    mode = payload.mode or conv.get("mode", "AUTO")
    thought = f"Analyzing intent for {mode} mode. Synthesizing grounded answer..."
    
    response_content = (
        f"**NOVA X Response ({mode} Mode)**:\n\n"
        f"I received your request: *\"{payload.content}\"*.\n\n"
        "Here are the key findings and recommendations:\n"
        "1. **Architecture Decoupling**: AI proposes actions, while the Policy Engine enforces strict permission barriers [1].\n"
        "2. **Real Verification**: System state is checked post-action to ensure deterministic accuracy [2].\n"
        "3. **Human Control**: Consequential operations require your explicit authorization."
    )

    citations = [
        CitationModel(
            id="cit-1",
            title="NOVA X Master Architecture",
            snippet="Decoupled policy engine and verification boundary.",
            source_url="docs/architecture.md",
            confidence_score=0.98
        ),
        CitationModel(
            id="cit-2",
            title="Verification Subsystem Specification",
            snippet="Zero-trust post-action inspection.",
            source_url="docs/architecture.md",
            confidence_score=0.95
        )
    ]

    asst_msg_doc = {
        "id": asst_msg_id,
        "conversation_id": id,
        "role": "assistant",
        "content": response_content,
        "mode": mode,
        "thought_process": thought,
        "citations": [c.model_dump() for c in citations],
        "created_at": asst_now_str,
    }
    await messages_col.insert_one(asst_msg_doc)
    await col.update_one({"id": id}, {"$set": {"updated_at": asst_now_str}})

    if not stream:
        return {
            "user_message": MessageResponse(**user_msg_doc),
            "assistant_message": MessageResponse(**asst_msg_doc)
        }

    # Stream as Server-Sent Events (SSE)
    async def event_generator():
        yield f"event: thought\ndata: {json.dumps({'thought': thought})}\n\n"
        await asyncio.sleep(0.05)

        # Stream words/tokens
        words = response_content.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.01)

        yield f"event: citations\ndata: {json.dumps({'citations': [c.model_dump() for c in citations]})}\n\n"
        yield f"event: done\ndata: {json.dumps({'message_id': asst_msg_id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/conversations/{id}/branch", response_model=ConversationDetailResponse)
async def branch_conversation(
    id: str,
    from_message_id: str = Query(...),
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    col = db.get_collection("conversations")
    messages_col = db.get_collection("messages")

    conv = await col.find_one({"id": id, "user_id": current_user["id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Original conversation not found")

    all_msgs = await messages_col.find({"conversation_id": id})
    all_msgs.sort(key=lambda x: x.get("created_at", ""))

    # Find slice up to from_message_id
    cutoff_index = -1
    for idx, m in enumerate(all_msgs):
        if m["id"] == from_message_id:
            cutoff_index = idx
            break

    if cutoff_index == -1:
        raise HTTPException(status_code=404, detail="Message to branch from not found")

    branched_msgs = all_msgs[:cutoff_index + 1]

    # Create new branched conversation
    new_conv_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()
    new_title = f"{conv.get('title', 'Chat')} (Branch)"

    new_conv_doc = {
        "id": new_conv_id,
        "user_id": current_user["id"],
        "title": new_title,
        "mode": conv.get("mode", "AUTO"),
        "project_id": conv.get("project_id"),
        "pinned": False,
        "archived": False,
        "created_at": now_str,
        "updated_at": now_str,
    }
    await col.insert_one(new_conv_doc)

    copied_messages = []
    for m in branched_msgs:
        copied_m = dict(m)
        copied_m["id"] = str(uuid.uuid4())
        copied_m["conversation_id"] = new_conv_id
        await messages_col.insert_one(copied_m)
        copied_messages.append(MessageResponse(**copied_m))

    return ConversationDetailResponse(
        **new_conv_doc,
        message_count=len(copied_messages),
        messages=copied_messages
    )
