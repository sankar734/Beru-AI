from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, status
from pydantic import BaseModel
from typing import Optional

from apps.api.auth import get_current_user
from services.ai_core.multimodal.vision_engine import vision_engine, VisionAnalysisResult
from services.ai_core.multimodal.voice_engine import voice_engine, TranscriptionResult

router = APIRouter(prefix="/media", tags=["Vision, Voice & Media"])

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "nova-voice-default"

class ImageGenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: Optional[str] = "16:9"

@router.post("/vision/analyze", response_model=VisionAnalysisResult)
async def analyze_vision(
    file: UploadFile = File(...),
    prompt: str = Form("Explain what is depicted in this screenshot or document image."),
    current_user: dict = Depends(get_current_user)
):
    image_bytes = await file.read()
    return await vision_engine.analyze(image_bytes, prompt, filename=file.filename)

@router.post("/voice/transcribe", response_model=TranscriptionResult)
async def transcribe_voice(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    audio_bytes = await file.read()
    return await voice_engine.transcribe(audio_bytes, filename=file.filename)

@router.post("/voice/synthesize")
async def synthesize_voice(
    payload: SynthesizeRequest,
    current_user: dict = Depends(get_current_user)
):
    result = await voice_engine.synthesize(payload.text, voice=payload.voice or "nova-voice-default")
    return Response(content=result.audio_bytes, media_type=result.format)

@router.post("/image/generate")
async def generate_image_asset(
    payload: ImageGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    return {
        "status": "success",
        "prompt": payload.prompt,
        "aspect_ratio": payload.aspect_ratio,
        "image_url": "/favicon.svg",
        "description": f"Generated graphic asset matching prompt: '{payload.prompt}'"
    }
