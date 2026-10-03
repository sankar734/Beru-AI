"""NOVA X - Code Execution API Router
Provides endpoints for sandboxed code execution, analysis, and templates.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from services.code_runner.sandbox import (
    sandbox_runner,
    CodeExecutionRequest,
    CodeExecutionResponse,
    CodeAnalysisResponse,
)
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/code", tags=["Code Workspace"])

CODE_TEMPLATES = {
    "python": [
        {
            "id": "py-data-stats",
            "name": "Statistical Summarizer",
            "description": "Compute mean, median, standard deviation on sample data",
            "code": (
                "import statistics\n\n"
                "data = [24, 45, 12, 89, 56, 73, 91, 18, 33, 47, 62]\n"
                "print('NOVA X Data Engine')\n"
                "print('-----------------')\n"
                "print(f'Count: {len(data)}')\n"
                "print(f'Mean:  {statistics.mean(data):.2f}')\n"
                "print(f'Median: {statistics.median(data)}')\n"
                "print(f'StDev:  {statistics.stdev(data):.2f}')\n"
            ),
        },
        {
            "id": "py-fibonacci",
            "name": "Memoized Fibonacci Sequence",
            "description": "High-performance recursion with LRU cache",
            "code": (
                "from functools import lru_cache\n"
                "import time\n\n"
                "@lru_cache(maxsize=None)\n"
                "def fib(n: int) -> int:\n"
                "    if n < 2:\n"
                "        return n\n"
                "    return fib(n-1) + fib(n-2)\n\n"
                "t0 = time.perf_counter()\n"
                "results = [fib(i) for i in range(30)]\n"
                "duration = (time.perf_counter() - t0) * 1000\n"
                "print(f'First 30 Fibonacci numbers computed in {duration:.3f}ms:')\n"
                "print(results)\n"
            ),
        },
    ],
    "javascript": [
        {
            "id": "js-async-pipeline",
            "name": "Async Task Pipeline",
            "description": "Simulate parallel processing with Promise.all",
            "code": (
                "console.log('NOVA X JavaScript Execution Runtime');\n"
                "console.log('====================================');\n\n"
                "const tasks = ['Fetch Market Rates', 'Parse Telemetry', 'Verify Signatures'];\n\n"
                "async function runPipeline() {\n"
                "  const results = await Promise.all(\n"
                "    tasks.map(async (name, i) => {\n"
                "      const delay = (i + 1) * 50;\n"
                "      return new Promise(resolve => {\n"
                "        setTimeout(() => resolve(`Task [${name}] done in ${delay}ms`), delay);\n"
                "      });\n"
                "    })\n"
                "  );\n"
                "  results.forEach(r => console.log('✓', r));\n"
                "  console.log('All pipeline tasks completed.');\n"
                "}\n\n"
                "runPipeline();\n"
            ),
        },
    ],
    "powershell": [
        {
            "id": "ps-env-info",
            "name": "Runtime Diagnostics",
            "description": "Inspect sandbox environment and basic platform details",
            "code": (
                "Write-Host 'NOVA X PowerShell Sandbox Diagnostics'\n"
                "Write-Host '===================================='\n"
                "Write-Host \"OS Version: $([System.Environment]::OSVersion)\"\n"
                "Write-Host \"Process Arch: $([System.Environment]::Is64BitProcess ? '64-bit' : '32-bit')\"\n"
                "Write-Host \"Sandbox Active: $env:NOVA_SANDBOX\"\n"
                "Write-Host 'Diagnostics complete.'\n"
            ),
        }
    ],
}


class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    req: CodeExecutionRequest,
    user=Depends(get_optional_user),
):
    """Executes code in an isolated sandbox with resource constraints and credential sanitization."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty.")
    return sandbox_runner.execute(req)


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    req: CodeAnalysisRequest,
    user=Depends(get_optional_user),
):
    """Performs static security and complexity analysis on submitted code."""
    return sandbox_runner.analyze(req.code, req.language)


@router.get("/templates")
async def get_templates():
    """Returns curated starter templates for sandbox programming."""
    return {"templates": CODE_TEMPLATES}
