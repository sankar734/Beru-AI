"""NOVA X - Base Tool and Verification Definitions
Implements the foundational contracts for AI tools, risk stratification, and state verification.
"""

from enum import IntEnum
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class ToolRiskLevel(IntEnum):
    LEVEL_0_PURE_COMPUTE = 0       # In-memory calculations, formatting, pure parsing
    LEVEL_1_READ_ONLY = 1          # Read file in sandbox, search web, query telemetry
    LEVEL_2_LOW_MUTATION = 2       # Write ephemeral scratch file, non-destructive temporary state
    LEVEL_3_CONSEQUENTIAL = 3      # Write/modify project file, outbound API call, git commit
    LEVEL_4_DANGEROUS = 4          # Host command, delete files, system configuration, kill process


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class VerificationResult(BaseModel):
    verified: bool
    details: str
    observed_state: Optional[Dict[str, Any]] = None


class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None
    verification: VerificationResult
    execution_duration_ms: float
    risk_level: int


class BaseTool(ABC):
    """Abstract base class for all tools in NOVA X."""

    def __init__(
        self,
        name: str,
        description: str,
        risk_level: ToolRiskLevel,
        parameters: List[ToolParameter],
    ):
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.parameters = parameters

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Any:
        """Executes the core action of the tool."""
        pass

    @abstractmethod
    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        """Verifies the physical side effects on the environment (e.g. disk/process/network)."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Returns the OpenAI/Anthropic compatible function schema."""
        properties = {}
        required = []
        for p in self.parameters:
            properties[p.name] = {
                "type": p.type,
                "description": p.description,
            }
            if p.required:
                required.append(p.name)

        return {
            "name": self.name,
            "description": self.description,
            "risk_level": int(self.risk_level),
            "requires_human_approval": self.risk_level >= ToolRiskLevel.LEVEL_3_CONSEQUENTIAL,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
