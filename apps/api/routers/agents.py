"""NOVA X - Autonomous Agent Execution API Router
Provides endpoints to trigger autonomous multi-step missions, inspect real-time trajectories,
and authorize consequential actions.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from services.ai_core.agents.models import AgentRun, AgentRunCreate, AgentStatus
from services.ai_core.agents.agent_runner import agent_runner
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/agents", tags=["Autonomous Agents"])


class AgentApprovalAction(BaseModel):
    approved: bool


@router.post("/run", response_model=AgentRun)
async def launch_agent_mission(
    payload: AgentRunCreate,
    user=Depends(get_optional_user),
):
    """Launches an autonomous agent mission, executing until completion or human approval pause."""
    user_id = user["id"] if user else "default"
    run = await agent_runner.start_run(
        goal=payload.goal,
        mode=payload.mode,
        max_steps=payload.max_steps,
        user_id=user_id,
    )
    return run


@router.get("/runs", response_model=List[AgentRun])
async def list_agent_runs(
    user=Depends(get_optional_user),
):
    """Lists all active and previous agent runs."""
    user_id = user["id"] if user else "default"
    return agent_runner.list_runs(user_id=user_id)


@router.get("/runs/{run_id}", response_model=AgentRun)
async def get_agent_run(
    run_id: str,
    user=Depends(get_optional_user),
):
    """Retrieves full trajectory and step-by-step state verification for an agent mission."""
    run = agent_runner.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found.")
    return run


@router.post("/runs/{run_id}/approve", response_model=AgentRun)
async def authorize_agent_action(
    run_id: str,
    payload: AgentApprovalAction,
    user=Depends(get_optional_user),
):
    """Authorizes or rejects a paused consequential step in an autonomous agent mission."""
    try:
        updated_run = await agent_runner.resume_run(run_id, approved=payload.approved)
        return updated_run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
