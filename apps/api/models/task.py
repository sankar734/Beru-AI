"""NOVA X - Tasks and Long-Horizon Goals Models
Data models for strategic goals, prioritized task lifecycles, and autonomous agent dispatching.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = ""
    target_date: Optional[str] = None


class GoalResponse(GoalCreate):
    id: str
    user_id: str
    progress_percent: float = 0.0
    tasks_count: int = 0
    completed_tasks_count: int = 0
    created_at: str
    updated_at: str


class TaskCreate(BaseModel):
    goal_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None
    assigned_agent_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    goal_id: Optional[str]
    user_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[str]
    assigned_agent_id: Optional[str]
    created_at: str
    updated_at: str
