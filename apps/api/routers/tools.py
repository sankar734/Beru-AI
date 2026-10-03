"""NOVA X - Tools & Zero-Trust Policy API Router
Endpoints for tool introspection, action proposal risk analysis, human approval, and verified execution.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from services.ai_core.tools.policy_engine import (
    tool_registry,
    policy_engine,
    ProposalEvaluation,
    ApprovalRequest,
    ToolResult,
)
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/tools", tags=["Tool Registry & Policy"])


class ActionProposalRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class ActionApprovalDecision(BaseModel):
    request_id: str
    approved: bool


class ActionExecutionRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    approval_token: Optional[str] = None


@router.get("")
async def list_tools():
    """Lists all registered tools, their schemas, and assigned risk levels."""
    return {"tools": tool_registry.list_all()}


@router.post("/propose", response_model=ProposalEvaluation)
async def propose_action(
    req: ActionProposalRequest,
    user=Depends(get_optional_user),
):
    """Evaluates a proposed tool action against the Zero-Trust Policy Barrier."""
    try:
        user_id = user["id"] if user else "default"
        return policy_engine.propose_action(req.tool_name, req.params, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/approve", response_model=ApprovalRequest)
async def decide_action_approval(
    req: ActionApprovalDecision,
    user=Depends(get_optional_user),
):
    """Grants or denies human operator authorization for a Level 3 or 4 action."""
    try:
        return policy_engine.decide_approval(req.request_id, req.approved)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/execute", response_model=ToolResult)
async def execute_tool(
    req: ActionExecutionRequest,
    user=Depends(get_optional_user),
):
    """Executes a tool action with post-action verification and policy enforcement."""
    try:
        result = await policy_engine.execute_tool(
            tool_name=req.tool_name,
            params=req.params,
            approval_token=req.approval_token,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
