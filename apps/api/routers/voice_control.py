import base64
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from apps.api.auth import get_optional_user
from services.desktop_companion.voice_control import voice_action_controller, VoiceActionProposal
from services.ai_core.multimodal.voice_engine import voice_engine

logger = logging.getLogger("nova.api.voice_control")

router = APIRouter(prefix="/voice", tags=["Voice Desktop Control"])

class VoiceCommandRequest(BaseModel):
    command_text: Optional[str] = None
    audio_base64: Optional[str] = None
    synthesize_response: bool = True

class VoiceConfirmRequest(BaseModel):
    action_id: str
    confirmed: bool = True

class VoiceCommandResponse(BaseModel):
    action_id: str
    command_text: str
    intent: str
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    risk_level: int
    requires_confirmation: bool
    status: str
    result: Optional[Any] = None
    voice_feedback_text: str
    audio_response_base64: Optional[str] = None

@router.post("/command", response_model=VoiceCommandResponse)
async def process_voice_command(
    req: VoiceCommandRequest,
    user: Optional[dict] = Depends(get_optional_user)
):
    """Processes speech or text voice command and executes safe desktop action or stages confirmation."""
    audio_bytes = None
    if req.audio_base64:
        try:
            audio_bytes = base64.b64decode(req.audio_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid audio_base64 encoding")

    proposal = await voice_action_controller.process_voice_command(
        command_text=req.command_text,
        audio_bytes=audio_bytes
    )

    audio_res_b64 = None
    if req.synthesize_response and proposal.voice_feedback_text:
        try:
            synth = await voice_engine.synthesize(proposal.voice_feedback_text)
            audio_res_b64 = base64.b64encode(synth.audio_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"Voice synthesis skipped: {e}")

    return VoiceCommandResponse(
        action_id=proposal.action_id,
        command_text=proposal.command_text,
        intent=proposal.intent,
        tool_name=proposal.tool_name,
        params=proposal.params,
        risk_level=proposal.risk_level,
        requires_confirmation=proposal.requires_confirmation,
        status=proposal.status,
        result=proposal.result,
        voice_feedback_text=proposal.voice_feedback_text,
        audio_response_base64=audio_res_b64
    )

@router.post("/confirm", response_model=VoiceCommandResponse)
async def confirm_voice_action(
    req: VoiceConfirmRequest,
    user: Optional[dict] = Depends(get_optional_user)
):
    """Authorizes or cancels a staged Level 3/4 action."""
    try:
        proposal = await voice_action_controller.confirm_action(req.action_id, req.confirmed)
        
        audio_res_b64 = None
        if proposal.voice_feedback_text:
            try:
                synth = await voice_engine.synthesize(proposal.voice_feedback_text)
                audio_res_b64 = base64.b64encode(synth.audio_bytes).decode("utf-8")
            except Exception:
                pass

        return VoiceCommandResponse(
            action_id=proposal.action_id,
            command_text=proposal.command_text,
            intent=proposal.intent,
            tool_name=proposal.tool_name,
            params=proposal.params,
            risk_level=proposal.risk_level,
            requires_confirmation=proposal.requires_confirmation,
            status=proposal.status,
            result=proposal.result,
            voice_feedback_text=proposal.voice_feedback_text,
            audio_response_base64=audio_res_b64
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[VoiceActionProposal])
async def get_voice_history(
    limit: int = 20,
    user: Optional[dict] = Depends(get_optional_user)
):
    """Retrieves recent voice control actions."""
    return voice_action_controller.get_history(limit=limit)
