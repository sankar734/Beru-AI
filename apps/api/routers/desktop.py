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
from services.desktop_companion.window_manager import (
    window_manager,
    WindowItem,
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


class SendKeysPayload(BaseModel):
    text: str


@router.get("/windows", response_model=List[WindowItem])
async def list_desktop_windows(user=Depends(get_optional_user)):
    """Enumerates visible top-level windows on the host desktop."""
    return window_manager.list_windows()


@router.post("/windows/{hwnd}/focus")
async def focus_desktop_window(hwnd: int, user=Depends(get_optional_user)):
    """Brings a window to the foreground."""
    success = window_manager.focus_window(hwnd)
    return {"status": "success" if success else "failed", "hwnd": hwnd}


@router.post("/windows/{hwnd}/send-keys")
async def send_keys_to_window(
    hwnd: int,
    payload: SendKeysPayload,
    user=Depends(get_optional_user),
):
    """Sends keystrokes to target window with focus management."""
    result = window_manager.send_keys(hwnd, payload.text)
    return result
