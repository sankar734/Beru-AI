"""NOVA X - Tasks and Long-Horizon Goals Router
Manages strategic objectives, prioritized task backlogs, and autonomous agent delegation.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from apps.api.database import db_manager
from apps.api.auth import get_optional_user
from apps.api.models.task import (
    GoalCreate,
    GoalResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatus,
    TaskPriority,
)
from services.ai_core.agents.agent_runner import agent_runner

router = APIRouter(prefix="/tasks", tags=["Tasks & Goals"])

DEFAULT_GOALS = [
    {
        "id": "goal-nova-release",
        "user_id": "default",
        "title": "NOVA X Full-Spectrum Personal Intelligence OS Deployment",
        "description": "Complete production build of all 28 architectural phases with zero mock shortcuts.",
        "target_date": "2026-11-01",
        "progress_percent": 65.0,
        "tasks_count": 5,
        "completed_tasks_count": 3,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
]

DEFAULT_TASKS = [
    {
        "id": "task-sec-cert",
        "goal_id": "goal-nova-release",
        "user_id": "default",
        "title": "Run zero-trust security audit and verify permission policy barriers",
        "description": "Ensure cloud AI cannot execute unverified shell commands without human confirmation.",
        "status": "TODO",
        "priority": "HIGH",
        "due_date": "2026-10-15",
        "assigned_agent_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "task-perf-profile",
        "goal_id": "goal-nova-release",
        "user_id": "default",
        "title": "Profile async database queries and client bundle size",
        "description": "Verify sub-millisecond response latency and clean tree-shaken assets.",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "due_date": "2026-10-20",
        "assigned_agent_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "task-arch-spec",
        "goal_id": "goal-nova-release",
        "user_id": "default",
        "title": "Finalize 40-point architectural specification",
        "description": "Exhaustive documentation of all OS interfaces, pipelines, and security layers.",
        "status": "COMPLETED",
        "priority": "HIGH",
        "due_date": "2026-10-05",
        "assigned_agent_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


async def ensure_defaults():
    g_col = db_manager.get_collection("goals")
    if await g_col.count_documents({}) == 0:
        for g in DEFAULT_GOALS:
            await g_col.insert_one(g)

    t_col = db_manager.get_collection("tasks")
    if await t_col.count_documents({}) == 0:
        for t in DEFAULT_TASKS:
            await t_col.insert_one(t)


@router.get("/goals", response_model=List[GoalResponse])
async def list_goals(user=Depends(get_optional_user)):
    """Lists strategic goals."""
    await ensure_defaults()
    col = db_manager.get_collection("goals")
    user_id = user["id"] if user else "default"
    docs = await col.find({"$or": [{"user_id": user_id}, {"user_id": "default"}]})
    for d in docs:
        d.pop("_id", None)
    return docs


@router.post("/goals", response_model=GoalResponse)
async def create_goal(payload: GoalCreate, user=Depends(get_optional_user)):
    """Creates a strategic goal."""
    col = db_manager.get_collection("goals")
    user_id = user["id"] if user else "default"
    goal_id = f"goal-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": goal_id,
        "user_id": user_id,
        "title": payload.title,
        "description": payload.description or "",
        "target_date": payload.target_date,
        "progress_percent": 0.0,
        "tasks_count": 0,
        "completed_tasks_count": 0,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    await col.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    goal_id: Optional[str] = None,
    status: Optional[str] = None,
    user=Depends(get_optional_user),
):
    """Lists tasks with optional goal or status filter."""
    await ensure_defaults()
    col = db_manager.get_collection("tasks")
    user_id = user["id"] if user else "default"
    query: Dict[str, Any] = {"$or": [{"user_id": user_id}, {"user_id": "default"}]}
    if goal_id:
        query["goal_id"] = goal_id
    if status:
        query["status"] = status.upper()

    docs = await col.find(query)
    for d in docs:
        d.pop("_id", None)
    return docs


@router.post("", response_model=TaskResponse)
async def create_task(payload: TaskCreate, user=Depends(get_optional_user)):
    """Creates a task."""
    col = db_manager.get_collection("tasks")
    user_id = user["id"] if user else "default"
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": task_id,
        "goal_id": payload.goal_id,
        "user_id": user_id,
        "title": payload.title,
        "description": payload.description or "",
        "status": TaskStatus.TODO.value,
        "priority": payload.priority.value,
        "due_date": payload.due_date,
        "assigned_agent_id": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    await col.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, payload: TaskUpdate, user=Depends(get_optional_user)):
    """Updates a task."""
    col = db_manager.get_collection("tasks")
    task = await col.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    update_dict: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
            update_dict[k] = v.value if hasattr(v, "value") else v

    await col.update_one({"id": task_id}, {"$set": update_dict})
    updated = await col.find_one({"id": task_id})
    updated.pop("_id", None)
    return updated


@router.delete("/{task_id}")
async def delete_task(task_id: str, user=Depends(get_optional_user)):
    """Deletes a task."""
    col = db_manager.get_collection("tasks")
    res = await col.delete_one({"id": task_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "message": f"Task {task_id} deleted."}


@router.post("/{task_id}/dispatch-agent", response_model=Dict[str, Any])
async def dispatch_agent_for_task(task_id: str, user=Depends(get_optional_user)):
    """Delegates a task to an autonomous agent to execute and update progress."""
    col = db_manager.get_collection("tasks")
    task = await col.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    user_id = user["id"] if user else "default"

    # Start agent run
    agent_run = await agent_runner.start_run(
        goal=task["title"],
        mode="AUTONOMOUS",
        max_steps=5,
        user_id=user_id,
    )

    new_status = TaskStatus.COMPLETED.value if agent_run.status == "COMPLETED" else TaskStatus.IN_PROGRESS.value

    await col.update_one(
        {"id": task_id},
        {
            "$set": {
                "assigned_agent_id": agent_run.id,
                "status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

    return {
        "task_id": task_id,
        "task_status": new_status,
        "agent_run_id": agent_run.id,
        "agent_status": agent_run.status,
    }
