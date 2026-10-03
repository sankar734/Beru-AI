import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel

from apps.api.config import settings
from apps.api.database import get_db, DatabaseManager
from apps.api.auth import get_current_user
from services.ai_core.rag.extractor import document_extractor
from services.ai_core.rag.chunker import text_chunker
from services.ai_core.rag.vector_store import get_vector_store, VectorRecord
from services.ai_core.rag.hybrid_retriever import get_hybrid_retriever, HybridRetriever, GroundedChunk
from services.ai_core.registry import get_provider_registry

router = APIRouter(prefix="/files", tags=["File Intelligence & RAG"])

class FileRecordResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_size: int
    mime_type: str
    chunk_count: int
    project_id: Optional[str] = None
    created_at: str

class RAGQueryRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    top_k: Optional[int] = 5

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    grounded_chunks: List[GroundedChunk]

@router.post("/upload", response_model=FileRecordResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    storage_dir = settings.STORAGE_LOCAL_DIR
    os.makedirs(storage_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    safe_filename = os.path.basename(file.filename or "upload.txt")
    dest_path = os.path.join(storage_dir, f"{file_id}_{safe_filename}")

    # 1. Write file to disk
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(dest_path)
    mime_type = file.content_type or "text/plain"

    # 2. Extract text & chunk
    text_content = document_extractor.extract_text(dest_path, mime_type)
    chunks = text_chunker.chunk_text(text_content)

    # 3. Generate embeddings & index into Vector Store
    if chunks:
        provider = get_provider_registry().get_provider("mock")
        chunk_texts = [c.text for c in chunks]
        embeddings = await provider.generate_embeddings(chunk_texts)

        vector_records = []
        for c, emb in zip(chunks, embeddings):
            v_id = f"{file_id}_{c.chunk_index}"
            vector_records.append(VectorRecord(
                id=v_id,
                vector=emb,
                payload={
                    "file_id": file_id,
                    "user_id": current_user["id"],
                    "project_id": project_id,
                    "file_name": safe_filename,
                    "page_number": c.page_number,
                    "section_title": c.section_title,
                    "chunk_index": c.chunk_index,
                    "text": c.text,
                }
            ))

        await get_vector_store().upsert("nova_rag_chunks", vector_records)

    # 4. Save metadata in DB
    now_str = datetime.now(timezone.utc).isoformat()
    file_doc = {
        "id": file_id,
        "user_id": current_user["id"],
        "file_name": safe_filename,
        "file_size": file_size,
        "mime_type": mime_type,
        "storage_path": dest_path,
        "chunk_count": len(chunks),
        "project_id": project_id,
        "created_at": now_str,
    }

    files_col = db.get_collection("files")
    await files_col.insert_one(file_doc)

    return FileRecordResponse(**file_doc)

@router.get("", response_model=List[FileRecordResponse])
async def list_files(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    files_col = db.get_collection("files")
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id

    docs = await files_col.find(query)
    return [FileRecordResponse(**d) for d in docs]

@router.delete("/{id}")
async def delete_file(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    files_col = db.get_collection("files")
    doc = await files_col.find_one({"id": id, "user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete local file
    if os.path.exists(doc.get("storage_path", "")):
        try:
            os.remove(doc["storage_path"])
        except OSError:
            pass

    # Delete vector records
    await get_vector_store().delete_by_file_id("nova_rag_chunks", id)

    # Delete DB doc
    await files_col.delete_one({"id": id})
    return {"message": "File deleted and vector records removed", "id": id}

@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag(
    payload: RAGQueryRequest,
    current_user: dict = Depends(get_current_user),
    retriever: HybridRetriever = Depends(get_hybrid_retriever)
):
    filter_payload = {"user_id": current_user["id"]}
    if payload.project_id:
        filter_payload["project_id"] = payload.project_id

    chunks = await retriever.retrieve(
        query=payload.query,
        collection_name="nova_rag_chunks",
        filter_payload=filter_payload,
        top_k=payload.top_k or 5
    )

    if not chunks:
        return RAGQueryResponse(
            query=payload.query,
            answer="No relevant documents or passages were found in your knowledge store for this query.",
            grounded_chunks=[]
        )

    # Synthesize grounded answer
    citations_text = []
    for i, c in enumerate(chunks[:3]):
        citations_text.append(f"[{i+1}] *{c.file_name}* (Page {c.page_number}, Section: {c.section_title})")

    answer = (
        f"Grounded answer synthesized from your private documents for: **\"{payload.query}\"**:\n\n"
        f"• **Primary Passage**: \"{chunks[0].text[:300]}...\" [1]\n"
    )
    if len(chunks) > 1:
        answer += f"• **Supporting Details**: \"{chunks[1].text[:250]}...\" [2]\n"

    answer += f"\nVerified citations: {', '.join(citations_text)}."

    return RAGQueryResponse(
        query=payload.query,
        answer=answer,
        grounded_chunks=chunks
    )
