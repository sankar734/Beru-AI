"""NOVA X - Desktop File Intelligence Router
Endpoints for approved directory introspection, local indexing, and workspace search.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from services.desktop_companion.file_indexer import (
    desktop_file_indexer,
    IndexedFileItem,
)
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/desktop/files", tags=["Desktop File Intelligence"])


class IndexRequest(BaseModel):
    root_path: str = Field(default=r"d:\5536\Projects\Beru")
    max_files: int = Field(default=100, ge=1, le=500)


@router.get("/roots")
async def list_approved_roots(user=Depends(get_optional_user)):
    """Lists the approved workspace directory roots."""
    return {"allowed_roots": desktop_file_indexer.allowed_roots}


@router.post("/index", response_model=List[IndexedFileItem])
async def index_directory(req: IndexRequest, user=Depends(get_optional_user)):
    """Indexes files within an approved workspace root."""
    try:
        return desktop_file_indexer.index_directory(req.root_path, req.max_files)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/search", response_model=List[IndexedFileItem])
async def search_files(
    query: str = Query(..., min_length=1),
    root_path: str = Query(default=r"d:\5536\Projects\Beru"),
    limit: int = Query(default=20, ge=1, le=100),
    user=Depends(get_optional_user),
):
    """Searches filenames and text content within approved workspace directories."""
    try:
        return desktop_file_indexer.search_local_files(query, root_path, limit)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
