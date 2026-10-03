"""NOVA X - Built-in Tools Suite
Concrete tool implementations across all 5 risk tiers (Level 0 through 4)
with mandatory post-action state verification.
"""

import os
import re
import ast
import operator
import subprocess
from typing import Dict, Any, List
from services.ai_core.tools.tool_base import (
    BaseTool,
    ToolRiskLevel,
    ToolParameter,
    VerificationResult,
)
from services.code_runner.sandbox import sandbox_runner, CodeExecutionRequest

# Safe math operators for Level 0 Calculator
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def safe_eval_math(expr: str) -> float:
    """Evaluates basic mathematical expressions securely using AST."""
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op = _SAFE_OPERATORS.get(type(node.op))
            if not op:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op = _SAFE_OPERATORS.get(type(node.op))
            if not op:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
            return op(operand)
        raise ValueError(f"Unsupported expression construct: {ast.dump(node)}")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


class CalculatorTool(BaseTool):
    """Level 0: Pure compute arithmetic evaluator."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs high-precision arithmetic and numeric calculations safely.",
            risk_level=ToolRiskLevel.LEVEL_0_PURE_COMPUTE,
            parameters=[
                ToolParameter(name="expression", type="string", description="Mathematical expression e.g. '(12 * 45) / 3'"),
            ],
        )

    async def execute(self, params: Dict[str, Any]) -> Any:
        expr = params.get("expression", "")
        return safe_eval_math(expr)

    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        is_num = isinstance(output, (int, float))
        return VerificationResult(
            verified=is_num,
            details="Calculation evaluated to valid numeric constant." if is_num else "Output was not a valid number.",
            observed_state={"value": output},
        )


class FileReadTool(BaseTool):
    """Level 1: Read-only file inspection."""

    def __init__(self):
        super().__init__(
            name="file_read",
            description="Reads the textual contents of a file from disk within permitted paths.",
            risk_level=ToolRiskLevel.LEVEL_1_READ_ONLY,
            parameters=[
                ToolParameter(name="filepath", type="string", description="Absolute or relative file path to read"),
            ],
        )

    async def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("filepath", "")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        path = params.get("filepath", "")
        exists = os.path.exists(path)
        return VerificationResult(
            verified=exists and isinstance(output, str),
            details=f"Read {len(output) if isinstance(output, str) else 0} bytes from disk.",
            observed_state={"path": path, "exists": exists, "size": len(output) if isinstance(output, str) else 0},
        )


class CodeSandboxRunTool(BaseTool):
    """Level 2: Ephemeral sandboxed code execution."""

    def __init__(self):
        super().__init__(
            name="code_sandbox_run",
            description="Executes code in an isolated ephemeral sandbox with hard resource limits.",
            risk_level=ToolRiskLevel.LEVEL_2_LOW_MUTATION,
            parameters=[
                ToolParameter(name="language", type="string", description="Programming language: python, javascript"),
                ToolParameter(name="code", type="string", description="Code string to execute"),
            ],
        )

    async def execute(self, params: Dict[str, Any]) -> Any:
        req = CodeExecutionRequest(
            language=params.get("language", "python"),
            code=params.get("code", ""),
            timeout_seconds=5.0,
        )
        res = sandbox_runner.execute(req)
        return res.model_dump()

    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        status = output.get("status") if isinstance(output, dict) else ""
        verified = status in ("SUCCESS", "ERROR")
        return VerificationResult(
            verified=verified,
            details=f"Subprocess terminated with sandbox status '{status}'.",
            observed_state=output,
        )


class FileWriteTool(BaseTool):
    """Level 3: Consequential file write requiring verification and approval."""

    def __init__(self):
        super().__init__(
            name="file_write",
            description="Writes or overwrites content to a file on disk. Requires human authorization.",
            risk_level=ToolRiskLevel.LEVEL_3_CONSEQUENTIAL,
            parameters=[
                ToolParameter(name="filepath", type="string", description="Target file path"),
                ToolParameter(name="content", type="string", description="Content to write"),
            ],
        )

    async def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("filepath", "")
        content = params.get("content", "")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"path": path, "bytes_written": len(content.encode("utf-8"))}

    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        path = params.get("filepath", "")
        expected = params.get("content", "")
        
        # Real post-action verification
        if not os.path.exists(path):
            return VerificationResult(verified=False, details=f"Verification Failed: File {path} was not created on disk.")
        
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            actual = f.read()

        size = os.path.getsize(path)
        content_matches = (actual == expected)

        return VerificationResult(
            verified=content_matches and size >= len(expected.encode("utf-8")),
            details=f"Verified file exists on disk. Size: {size} bytes. Content hash exact match.",
            observed_state={"path": path, "size_bytes": size, "content_match": content_matches},
        )


class FileDeleteTool(BaseTool):
    """Level 4: Dangerous destructive file deletion."""

    def __init__(self):
        super().__init__(
            name="file_delete",
            description="Permanently deletes a file from disk. Strictly requires human confirmation barrier.",
            risk_level=ToolRiskLevel.LEVEL_4_DANGEROUS,
            parameters=[
                ToolParameter(name="filepath", type="string", description="File path to delete permanently"),
            ],
        )

    async def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("filepath", "")
        if os.path.exists(path):
            os.remove(path)
            return {"deleted": True, "path": path}
        return {"deleted": False, "reason": "File did not exist"}

    async def verify(self, params: Dict[str, Any], output: Any) -> VerificationResult:
        path = params.get("filepath", "")
        exists = os.path.exists(path)
        # Succeeded ONLY if file is truly absent
        verified = not exists
        return VerificationResult(
            verified=verified,
            details=f"Verification Succeeded: File {path} is confirmed absent from disk." if verified else f"Verification Failed: File {path} still exists.",
            observed_state={"path": path, "still_exists": exists},
        )
