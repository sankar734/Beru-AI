"""NOVA X - Zero-Trust Policy Engine
Enforces the mandatory human approval barrier for Risk Levels 3 and 4,
and coordinates post-action state verification.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from services.ai_core.tools.tool_base import (
    BaseTool,
    ToolRiskLevel,
    ToolResult,
    VerificationResult,
)
from services.ai_core.tools.builtin_tools import (
    CalculatorTool,
    FileReadTool,
    CodeSandboxRunTool,
    FileWriteTool,
    FileDeleteTool,
)


class ApprovalRequest(BaseModel):
    request_id: str
    tool_name: str
    params: Dict[str, Any]
    risk_level: int
    reason: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXPIRED
    approval_token: Optional[str] = None
    created_at: str
    expires_at: str


class ProposalEvaluation(BaseModel):
    tool_name: str
    risk_level: int
    requires_approval: bool
    approval_request: Optional[ApprovalRequest] = None
    message: str


class ToolRegistry:
    """Registry maintaining active tool definitions."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(CalculatorTool())
        self.register(FileReadTool())
        self.register(CodeSandboxRunTool())
        self.register(FileWriteTool())
        self.register(FileDeleteTool())

    def register(self, tool: BaseTool):
        self._tools[tool.name.lower()] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name.lower())

    def list_all(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]


class PolicyEngine:
    """Zero-Trust Policy Barrier governing all tool invocations."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self._pending_approvals: Dict[str, ApprovalRequest] = {}

    def propose_action(
        self,
        tool_name: str,
        params: Dict[str, Any],
        user_id: str = "default",
    ) -> ProposalEvaluation:
        """Evaluates tool invocation against risk matrix."""
        tool = self.registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not registered in NOVA Tool Registry.")

        risk_val = int(tool.risk_level)
        requires_approval = (tool.risk_level >= ToolRiskLevel.LEVEL_3_CONSEQUENTIAL)

        if not requires_approval:
            return ProposalEvaluation(
                tool_name=tool.name,
                risk_level=risk_val,
                requires_approval=False,
                message="Tool is Level 0-2 (Read-Only/Pure Compute/Isolated Sandbox). Automatic execution allowed.",
            )

        req_id = f"apr-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=10)

        approval = ApprovalRequest(
            request_id=req_id,
            tool_name=tool.name,
            params=params,
            risk_level=risk_val,
            reason=f"Action '{tool.name}' is categorized as Risk Level {risk_val} (Consequential / Destructive).",
            status="PENDING",
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )
        self._pending_approvals[req_id] = approval

        return ProposalEvaluation(
            tool_name=tool.name,
            risk_level=risk_val,
            requires_approval=True,
            approval_request=approval,
            message="Action requires explicit human authorization before execution.",
        )

    def decide_approval(
        self,
        request_id: str,
        approved: bool,
    ) -> ApprovalRequest:
        """Human operator grants or denies permission for Level 3/4 action."""
        req = self._pending_approvals.get(request_id)
        if not req:
            raise ValueError(f"Approval request '{request_id}' not found or expired.")

        if approved:
            req.status = "APPROVED"
            req.approval_token = f"tok-{uuid.uuid4().hex}"
        else:
            req.status = "REJECTED"

        return req

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        approval_token: Optional[str] = None,
    ) -> ToolResult:
        """Executes a tool and performs mandatory state verification."""
        tool = self.registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")

        # Enforcement barrier for Level 3 and 4
        if tool.risk_level >= ToolRiskLevel.LEVEL_3_CONSEQUENTIAL:
            # Must have valid approved token
            valid_approval = any(
                req.approval_token == approval_token and req.status == "APPROVED"
                for req in self._pending_approvals.values()
            )
            if not valid_approval:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"SECURITY_VIOLATION: Tool '{tool_name}' (Risk Level {int(tool.risk_level)}) requires approved authorization token.",
                    verification=VerificationResult(
                        verified=False,
                        details="Execution preempted by NOVA Zero-Trust Policy Barrier.",
                    ),
                    execution_duration_ms=0.0,
                    risk_level=int(tool.risk_level),
                )

        # Run action
        t0 = time.perf_counter()
        try:
            output = await tool.execute(params)
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)

            # Mandatory Post-Action State Verification
            verification = await tool.verify(params, output)

            return ToolResult(
                success=verification.verified,
                output=output,
                error=None if verification.verified else f"Verification assertion failed: {verification.details}",
                verification=verification,
                execution_duration_ms=duration_ms,
                risk_level=int(tool.risk_level),
            )

        except Exception as e:
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                verification=VerificationResult(
                    verified=False,
                    details=f"Execution error: {str(e)}",
                ),
                execution_duration_ms=duration_ms,
                risk_level=int(tool.risk_level),
            )


# Global instances
tool_registry = ToolRegistry()
policy_engine = PolicyEngine(tool_registry)
