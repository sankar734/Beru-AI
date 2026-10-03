"""NOVA X - Autopilot & Proactive Intelligence Models
Data models for proactive recommendation cards, confidence scoring, and autopilot modes.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class AutopilotMode(str, Enum):
    FULL_AUTOPILOT = "FULL_AUTOPILOT"  # Level 0-2 actions run proactively; Level 3-4 prompt
    SUPERVISED = "SUPERVISED"          # Suggestions queue for operator review
    MANUAL = "MANUAL"                  # Autonomous monitors paused


class SuggestionCategory(str, Enum):
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    LEARNING = "LEARNING"
    MAINTENANCE = "MAINTENANCE"


class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AutopilotSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: f"sug-{uuid.uuid4().hex[:8]}")
    category: SuggestionCategory
    title: str
    description: str
    impact: ImpactLevel
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    action_tool: str
    action_params: Dict[str, Any] = Field(default_factory=dict)
    dismissed: bool = False
    applied: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AutopilotConfig(BaseModel):
    mode: AutopilotMode = AutopilotMode.FULL_AUTOPILOT
    active_monitors: List[str] = Field(
        default_factory=lambda: ["zero_trust_auditor", "latency_profiler", "learning_pacer"]
    )
    quiet_hours_enabled: bool = False
