"""NOVA X - Autonomous Agent Models
Data structures defining agent plans, execution steps, risk barriers, and trajectories.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


class AgentStep(BaseModel):
    step_number: int
    title: str
    thought: str
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    risk_level: int = 0
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    approval_token: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    status: str = "PENDING"  # PENDING, RUNNING, AWAITING_APPROVAL, COMPLETED, FAILED
    duration_ms: float = 0.0


class AgentRunCreate(BaseModel):
    goal: str = Field(..., min_length=3, max_length=500)
    mode: str = Field(default="AUTONOMOUS", description="AUTONOMOUS, DIRECTED, REASONING")
    max_steps: int = Field(default=8, ge=1, le=25)


class AgentRun(BaseModel):
    id: str = Field(default_factory=lambda: f"run-{uuid.uuid4().hex[:10]}")
    user_id: str = "default"
    goal: str
    mode: str = "AUTONOMOUS"
    status: AgentStatus = AgentStatus.INITIALIZING
    max_steps: int = 8
    current_step: int = 0
    steps: List[AgentStep] = Field(default_factory=list)
    final_summary: Optional[str] = None
    pending_approval_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
