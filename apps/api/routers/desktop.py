"""NOVA X - Desktop Companion API Router
Endpoints for live host telemetry, process inspection, application launching, and clipboard control.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from services.desktop_companion.daemon import (
    desktop_daemon,
    SystemVitals,
    ProcessInfo,
    APP_WHITELIST,
)
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/desktop", tags=["Desktop Companion"])


class LaunchAppRequest(BaseModel):
    app_key: str = Field(..., description="Whitelisted app: notepad, calc, explorer, powershell")


class ClipboardPayload(BaseModel):
    text: str


@router.get("/status", response_model=SystemVitals)
async def get_desktop_status(user=Depends(get_optional_user)):
    """Retrieves real-time host hardware vitals (CPU, RAM, Disk, OS)."""
    return desktop_daemon.get_vitals()


@router.get("/processes", response_model=List[ProcessInfo])
async def get_desktop_processes(
    limit: int = 15,
    user=Depends(get_optional_user),
):
    """Lists top running desktop processes sorted by memory usage."""
    return desktop_daemon.get_processes(limit=limit)


@router.get("/apps")
async def list_whitelisted_apps():
    """Lists safe whitelisted desktop applications."""
    return {"whitelist": list(APP_WHITELIST.keys())}


@router.post("/launch-app")
async def launch_desktop_app(
    req: LaunchAppRequest,
    user=Depends(get_optional_user),
):
    """Launches a whitelisted local desktop application."""
    try:
        return desktop_daemon.launch_app(req.app_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clipboard")
async def read_clipboard(user=Depends(get_optional_user)):
    """Reads current clipboard buffer."""
    return {"clipboard": desktop_daemon.read_clipboard()}


@router.post("/clipboard")
async def write_clipboard(payload: ClipboardPayload, user=Depends(get_optional_user)):
    """Writes text to clipboard buffer."""
    desktop_daemon.write_clipboard(payload.text)
    return {"status": "success", "length": len(payload.text)}
