"""NOVA X - Isolated Code Execution Sandbox
Executes Python, JavaScript, and Shell scripts with strict timeout, directory isolation,
and automatic credential redaction.
"""

import os
import re
import sys
import time
import shutil
import tempfile
import subprocess
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"AIza[0-9A-Za-z-_]{35}", re.IGNORECASE),
    re.compile(r"(?:api_key|secret|password|bearer|token)\s*[:=]\s*['\"]([^'\"]+)['\"]", re.IGNORECASE),
]

SAFE_ENV_VARS = {
    "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT",
    "LANG", "LC_ALL", "USERPROFILE", "HOMEPATH", "HOMEDRIVE", "NODE_PATH"
}

FORBIDDEN_PATTERNS = [
    r"rm\s+-rf\s+[/~]",
    r"Format-Volume",
    r"diskpart",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",  # Fork bomb
    r"os\.system\(['\"]rm\s+-rf",
    r"shutil\.rmtree\(['\"]/[^'\"]*['\"]",
]


class CodeExecutionRequest(BaseModel):
    language: str = Field(default="python", description="Language: python, javascript, bash, powershell")
    code: str = Field(..., description="Source code to execute")
    stdin: Optional[str] = Field(default="", description="Optional standard input to pass to process")
    timeout_seconds: float = Field(default=5.0, ge=0.5, le=15.0, description="Max execution timeout in seconds")


class CodeExecutionResponse(BaseModel):
    status: str  # SUCCESS, ERROR, TIMEOUT, BLOCKED
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    language: str
    security_warnings: List[str] = []


class CodeAnalysisResponse(BaseModel):
    is_safe: bool
    language: str
    warnings: List[str]
    line_count: int
    complexity_score: int


def sanitize_output(text: str) -> str:
    """Sanitizes sensitive tokens, keys, and credentials from program output."""
    if not text:
        return ""
    sanitized = text
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
    return sanitized


def scan_code_security(code: str, language: str) -> List[str]:
    """Scans code for dangerous calls before execution."""
    warnings: List[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append(f"Security Alert: Potentially dangerous system pattern detected ({pattern})")
    
    # Specific language checks
    if language.lower() in ("python", "py"):
        if "__import__('os').system" in code or "__import__('subprocess')" in code:
            warnings.append("Warning: Obfuscated system call detected")
    return warnings


class SandboxRunner:
    """Manages isolated code execution in ephemeral directories."""

    def __init__(self, default_timeout: float = 5.0):
        self.default_timeout = default_timeout

    def _prepare_env(self) -> Dict[str, str]:
        """Creates a sanitized environment stripped of secrets and credentials."""
        clean_env = {}
        for key, val in os.environ.items():
            if key.upper() in SAFE_ENV_VARS:
                clean_env[key] = val
        clean_env["PYTHONUNBUFFERED"] = "1"
        clean_env["NOVA_SANDBOX"] = "1"
        return clean_env

    def analyze(self, code: str, language: str = "python") -> CodeAnalysisResponse:
        """Performs static safety and complexity analysis on code."""
        warnings = scan_code_security(code, language)
        lines = code.splitlines()
        line_count = len(lines)
        
        # Simple complexity heuristic: control statements count
        complexity = 1
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(k) for k in ("if ", "for ", "while ", "try:", "except ", "switch ", "case ")):
                complexity += 1

        return CodeAnalysisResponse(
            is_safe=len(warnings) == 0,
            language=language,
            warnings=warnings,
            line_count=line_count,
            complexity_score=complexity,
        )

    def execute(self, req: CodeExecutionRequest) -> CodeExecutionResponse:
        """Executes code in an ephemeral sandbox directory."""
        lang = req.language.lower().strip()
        warnings = scan_code_security(req.code, lang)
        
        # If critical blocked pattern
        if any("Security Alert" in w for w in warnings):
            return CodeExecutionResponse(
                status="BLOCKED",
                stdout="",
                stderr="Execution blocked by NOVA Security Policy: Dangerous operation detected.",
                exit_code=-1,
                duration_ms=0.0,
                language=lang,
                security_warnings=warnings,
            )

        temp_dir = tempfile.mkdtemp(prefix="nova_sandbox_")
        start_time = time.perf_counter()

        try:
            env = self._prepare_env()
            cmd: List[str] = []
            script_file = ""

            if lang in ("python", "py"):
                script_file = os.path.join(temp_dir, "script.py")
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(req.code)
                cmd = [sys.executable, script_file]

            elif lang in ("javascript", "js", "node"):
                script_file = os.path.join(temp_dir, "script.js")
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(req.code)
                # Use node from path
                cmd = ["node", script_file]

            elif lang in ("bash", "sh"):
                script_file = os.path.join(temp_dir, "script.sh")
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(req.code)
                cmd = ["sh", script_file]

            elif lang in ("powershell", "ps1"):
                script_file = os.path.join(temp_dir, "script.ps1")
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write(req.code)
                cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_file]

            else:
                return CodeExecutionResponse(
                    status="ERROR",
                    stdout="",
                    stderr=f"Unsupported sandbox language: {lang}. Supported: python, javascript, powershell, bash.",
                    exit_code=-1,
                    duration_ms=0.0,
                    language=lang,
                    security_warnings=["Unsupported language"],
                )

            stdin_bytes = req.stdin.encode("utf-8") if req.stdin else None

            process = subprocess.run(
                cmd,
                input=stdin_bytes,
                capture_output=True,
                cwd=temp_dir,
                env=env,
                timeout=req.timeout_seconds,
            )
            
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            stdout = sanitize_output(process.stdout.decode("utf-8", errors="replace"))
            stderr = sanitize_output(process.stderr.decode("utf-8", errors="replace"))
            status = "SUCCESS" if process.returncode == 0 else "ERROR"

            return CodeExecutionResponse(
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                duration_ms=duration_ms,
                language=lang,
                security_warnings=warnings,
            )

        except subprocess.TimeoutExpired:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return CodeExecutionResponse(
                status="TIMEOUT",
                stdout="",
                stderr=f"Execution timed out after {req.timeout_seconds} seconds.",
                exit_code=-1,
                duration_ms=duration_ms,
                language=lang,
                security_warnings=["Timeout exceeded"],
            )
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return CodeExecutionResponse(
                status="ERROR",
                stdout="",
                stderr=f"Sandbox execution error: {str(e)}",
                exit_code=-1,
                duration_ms=duration_ms,
                language=lang,
                security_warnings=[str(e)],
            )
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass


# Global singleton
sandbox_runner = SandboxRunner()
