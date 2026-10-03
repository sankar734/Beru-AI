import re
import uuid
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from services.ai_core.multimodal.voice_engine import voice_engine
from services.desktop_companion.daemon import desktop_daemon
from services.desktop_companion.screen_capture import screen_engine
from services.desktop_companion.window_manager import window_manager
from services.desktop_companion.file_indexer import desktop_file_indexer

logger = logging.getLogger("nova.desktop.voice_control")

class VoiceActionProposal(BaseModel):
    action_id: str
    command_text: str
    intent: str
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    risk_level: int = 1
    requires_confirmation: bool = False
    status: str = "COMPLETED"  # COMPLETED, AWAITING_CONFIRMATION, CONFIRMED, REJECTED, FAILED
    result: Optional[Any] = None
    voice_feedback_text: str = ""
    audio_base64: Optional[str] = None

class VoiceActionController:
    """Orchestrates Speech-to-Action execution with zero-trust confirmation barriers."""

    def __init__(self):
        self._pending_actions: Dict[str, VoiceActionProposal] = {}
        self._history: List[VoiceActionProposal] = []

    def parse_intent(self, text: str) -> tuple[str, str, Dict[str, Any], int, str]:
        """
        Parses spoken command text into structured intent, target tool, parameters, risk level, and prompt.
        """
        clean = text.lower().strip()

        # 1. System Vitals & Hardware
        if any(k in clean for k in ["system status", "vitals", "cpu usage", "ram usage", "battery", "hardware"]):
            return (
                "SYSTEM_VITALS",
                "desktop_vitals",
                {},
                0,
                "Retrieving system vitals and performance statistics."
            )

        # 2. Screen Capture
        if any(k in clean for k in ["screenshot", "capture screen", "snapshot", "screen shot"]):
            return (
                "SCREEN_CAPTURE",
                "screen_capture",
                {"mask_sensitive": True},
                1,
                "Capturing current desktop screen with privacy masking."
            )

        # 3. Window Focus
        focus_match = re.search(r'(?:focus|switch to|bring up|activate)\s+([a-zA-Z0-9_\-\.\s]+)', clean)
        if focus_match:
            target_app = focus_match.group(1).strip()
            return (
                "WINDOW_FOCUS",
                "window_focus",
                {"title_query": target_app},
                1,
                f"Switching active foreground window to {target_app}."
            )

        # 4. App Launch (Risk Level 3 -> Requires Confirmation Barrier)
        launch_match = re.search(r'(?:open|launch|start|run)\s+(notepad|calculator|cmd|powershell|code|terminal|explorer)', clean)
        if launch_match:
            app_name = launch_match.group(1).strip()
            return (
                "APP_LAUNCH",
                "desktop_launch_app",
                {"app_key": app_name},
                3,
                f"Launching application {app_name} requires explicit confirmation."
            )

        # 5. File Search
        search_match = re.search(r'(?:search for|find file|locate file|look for)\s+([a-zA-Z0-9_\-\.\s]+)', clean)
        if search_match:
            query = search_match.group(1).strip()
            return (
                "FILE_SEARCH",
                "file_search",
                {"query": query},
                1,
                f"Searching local index for files matching {query}."
            )

        # 6. Fallback General Voice Query
        return (
            "GENERAL_QUERY",
            "ai_chat",
            {"query": text},
            0,
            f"Processing voice request: {text}"
        )

    async def process_voice_command(
        self,
        command_text: Optional[str] = None,
        audio_bytes: Optional[bytes] = None
    ) -> VoiceActionProposal:
        """Processes either speech audio or transcribed command into verified action."""
        if audio_bytes and not command_text:
            transcription = await voice_engine.transcribe(audio_bytes)
            command_text = transcription.transcript

        if not command_text:
            command_text = "Check system status"

        action_id = f"act_{uuid.uuid4().hex[:8]}"
        intent, tool_name, params, risk_level, feedback = self.parse_intent(command_text)

        requires_confirmation = risk_level >= 3

        proposal = VoiceActionProposal(
            action_id=action_id,
            command_text=command_text,
            intent=intent,
            tool_name=tool_name,
            params=params,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            status="AWAITING_CONFIRMATION" if requires_confirmation else "COMPLETED",
            voice_feedback_text=feedback
        )

        if not requires_confirmation:
            # Execute immediately for safe levels 0-2
            proposal.result = await self._execute_internal(tool_name, params)
            proposal.status = "COMPLETED"
        else:
            self._pending_actions[action_id] = proposal

        self._history.append(proposal)
        return proposal

    async def confirm_action(self, action_id: str, confirmed: bool) -> VoiceActionProposal:
        """Executes a staged Level 3/4 action following explicit confirmation."""
        if action_id not in self._pending_actions:
            raise KeyError(f"Action '{action_id}' not found or already processed.")

        proposal = self._pending_actions.pop(action_id)

        if not confirmed:
            proposal.status = "REJECTED"
            proposal.voice_feedback_text = f"Action '{proposal.intent}' was cancelled by the user."
            return proposal

        try:
            proposal.result = await self._execute_internal(proposal.tool_name, proposal.params)
            proposal.status = "CONFIRMED"
            proposal.voice_feedback_text = f"Action '{proposal.intent}' executed successfully."
        except Exception as e:
            proposal.status = "FAILED"
            proposal.voice_feedback_text = f"Execution failed: {str(e)}"

        return proposal

    async def _execute_internal(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Internal dispatch to desktop companion subsystem methods."""
        if tool_name == "desktop_vitals":
            vitals = desktop_daemon.get_vitals()
            return {
                "cpu_percent": vitals.cpu_percent,
                "ram_percent": vitals.ram_percent,
                "disk_percent": vitals.disk_percent
            }

        elif tool_name == "screen_capture":
            cap = screen_engine.capture()
            return {
                "width": cap.width,
                "height": cap.height,
                "has_image": len(cap.image_base64) > 0
            }

        elif tool_name == "window_focus":
            query = params.get("title_query", "").lower()
            windows = window_manager.list_windows()
            target_hwnd = None
            for w in windows:
                if query in w.title.lower():
                    target_hwnd = w.hwnd
                    break
            if target_hwnd:
                success = window_manager.focus_window(target_hwnd)
                return {"status": "focused", "hwnd": target_hwnd, "success": success}
            return {"status": "not_found", "query": query}

        elif tool_name == "desktop_launch_app":
            res = desktop_daemon.launch_app(params.get("app_key", "notepad"))
            return res


        elif tool_name == "file_search":
            results = desktop_file_indexer.search_files(params.get("query", ""), limit=5)
            return [r.model_dump() for r in results]

        elif tool_name == "ai_chat":
            return {"reply": f"Understood: '{params.get('query')}'"}

        return {"status": "unsupported_tool", "tool_name": tool_name}

    def get_history(self, limit: int = 20) -> List[VoiceActionProposal]:
        return self._history[-limit:]

voice_action_controller = VoiceActionController()
