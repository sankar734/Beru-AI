"""NOVA X - Screen Intelligence API Router
Endpoints for desktop screen capture, privacy redaction, and UI error diagnosis.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from services.desktop_companion.screen_capture import (
    screen_engine,
    ScreenCaptureResult,
)
from services.ai_core.multimodal.vision_engine import VisionAnalysisResult
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/desktop/screen", tags=["Screen Intelligence"])


class AnalyzeScreenRequest(BaseModel):
    image_base64: Optional[str] = None


@router.post("/capture", response_model=ScreenCaptureResult)
async def capture_screen(user=Depends(get_optional_user)):
    """Captures the active desktop screen with automated privacy sanitization."""
    return screen_engine.capture()


@router.post("/analyze", response_model=VisionAnalysisResult)
async def analyze_screen_capture(
    req: AnalyzeScreenRequest,
    user=Depends(get_optional_user),
):
    """Analyzes a desktop screenshot for UI elements, OCR text, and terminal errors."""
    return await screen_engine.analyze_screen(req.image_base64)
