"""NOVA X - Workflow Automation Models
Data models for directed acyclic graph (DAG) pipelines, node types, and execution traces.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class WorkflowNodeType(str, Enum):
    TRIGGER = "TRIGGER"
    AI_REASON = "AI_REASON"
    TOOL_EXECUTE = "TOOL_EXECUTE"
    CODE_SANDBOX = "CODE_SANDBOX"
    CONDITION = "CONDITION"
    OUTPUT = "OUTPUT"


class WorkflowNode(BaseModel):
    id: str
    name: str
    type: WorkflowNodeType
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = ""
    trigger_type: str = "MANUAL"  # MANUAL, SCHEDULE, WEBHOOK, EVENT
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)


class WorkflowResponse(WorkflowCreate):
    id: str
    user_id: str
    enabled: bool = True
    created_at: str
    updated_at: str


class NodeExecutionTrace(BaseModel):
    node_id: str
    node_name: str
    type: str
    status: str  # SUCCESS, FAILED, SKIPPED
    output: Any = None
    duration_ms: float = 0.0


class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    workflow_name: str
    status: str  # SUCCESS, FAILED
    traces: List[NodeExecutionTrace]
    duration_ms: float
    started_at: str
    completed_at: str
