import re
import sys
import time
import logging
import subprocess
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger("nova.developer.diagnostics")

class DiagnosticReport(BaseModel):
    has_error: bool
    error_type: Optional[str] = None
    target_file: Optional[str] = None
    target_line: Optional[int] = None
    raw_message: Optional[str] = None
    root_cause_summary: str
    remediation_steps: List[str] = []
    suggested_patch: Optional[str] = None

class TestRunResult(BaseModel):
    target: str
    exit_code: int
    success: bool
    passed_count: int = 0
    failed_count: int = 0
    duration_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""

class DiagnosticsEngine:
    """Automated Error Traceback Diagnostics and Test Runner."""

    def diagnose_traceback(self, log_text: str) -> DiagnosticReport:
        """Parses error tracebacks or build output and formulates a structured remediation report."""
        if not log_text or not log_text.strip():
            return DiagnosticReport(
                has_error=False,
                root_cause_summary="No log output or errors detected."
            )

        # 1. Check for Python Traceback
        if "Traceback (most recent call last):" in log_text or 'File "' in log_text:
            file_match = re.findall(r'File "([^"]+)", line (\d+)(?:, in (\w+))?', log_text)
            err_match = re.search(r'([A-Za-z_]+Error|Exception): (.+)', log_text)

            target_file = file_match[-1][0] if file_match else None
            target_line = int(file_match[-1][1]) if file_match else None
            err_type = err_match.group(1) if err_match else "PythonException"
            err_msg = err_match.group(2) if err_match else "Unhandled exception"

            remediation = [
                f"Inspect line {target_line} in {target_file}",
                f"Verify inputs, types, or imports associated with '{err_msg}'",
                "Execute isolated unit test to verify remediation"
            ]

            return DiagnosticReport(
                has_error=True,
                error_type=err_type,
                target_file=target_file,
                target_line=target_line,
                raw_message=f"{err_type}: {err_msg}",
                root_cause_summary=f"Python runtime exception '{err_type}' encountered at {target_file}:{target_line}",
                remediation_steps=remediation
            )

        # 2. Check for TypeScript / Vite compiler error
        ts_match = re.search(r'error TS(\d+):\s*(.+)', log_text)
        if ts_match:
            ts_code = ts_match.group(1)
            ts_msg = ts_match.group(2)
            file_loc = re.search(r'([a-zA-Z0-9_\-\./\\]+\.tsx?)\((\d+),(\d+)\)', log_text)
            
            target_file = file_loc.group(1) if file_loc else None
            target_line = int(file_loc.group(2)) if file_loc else None

            return DiagnosticReport(
                has_error=True,
                error_type=f"TypeScript TS{ts_code}",
                target_file=target_file,
                target_line=target_line,
                raw_message=ts_msg,
                root_cause_summary=f"TypeScript compilation error TS{ts_code}: {ts_msg}",
                remediation_steps=[
                    f"Check type definitions or exports at {target_file}:{target_line}",
                    "Ensure matching interface/type annotations are imported",
                    "Re-run 'npm run build' to confirm fix"
                ]
            )

        # 3. Check for Pytest failure
        if "FAILED " in log_text:
            fail_line = re.search(r'FAILED ([^:]+)::(test_[A-Za-z0-9_]+) - (.+)', log_text)
            if fail_line:
                test_file = fail_line.group(1)
                test_fn = fail_line.group(2)
                fail_reason = fail_line.group(3)
                return DiagnosticReport(
                    has_error=True,
                    error_type="PytestAssertionFailure",
                    target_file=test_file,
                    raw_message=fail_reason,
                    root_cause_summary=f"Test failure in {test_fn} ({test_file}): {fail_reason}",
                    remediation_steps=[
                        f"Review assertions in {test_file} for {test_fn}",
                        "Check backend return payload against expected schema",
                        "Run targeted pytest"
                    ]
                )

        return DiagnosticReport(
            has_error=False,
            root_cause_summary="Log inspected cleanly. No fatal exceptions or compiler errors detected."
        )

    def run_tests_sandboxed(self, target: str = "tests/test_phase0.py", timeout: int = 20) -> TestRunResult:
        """Executes a targeted pytest suite with strict timeout and output parsing."""
        t0 = time.time()
        # Security sanitization on target: must stay in tests/
        sanitized_target = target.strip().replace(";", "").replace("&", "").replace("|", "")
        if not sanitized_target.startswith("tests"):
            sanitized_target = "tests/test_phase0.py"

        cmd = [sys.executable, "-m", "pytest", sanitized_target, "-q"]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            elapsed = (time.time() - t0) * 1000
            stdout = res.stdout
            stderr = res.stderr

            passed = 0
            failed = 0
            # Parse pytest summary e.g. "3 passed in 0.5s" or "1 failed, 2 passed"
            passed_match = re.search(r'(\d+)\s+passed', stdout)
            failed_match = re.search(r'(\d+)\s+failed', stdout)

            if passed_match:
                passed = int(passed_match.group(1))
            if failed_match:
                failed = int(failed_match.group(1))

            return TestRunResult(
                target=sanitized_target,
                exit_code=res.returncode,
                success=(res.returncode == 0),
                passed_count=passed,
                failed_count=failed,
                duration_ms=round(elapsed, 2),
                stdout=stdout[:4000],
                stderr=stderr[:2000]
            )
        except subprocess.TimeoutExpired:
            return TestRunResult(
                target=sanitized_target,
                exit_code=-1,
                success=False,
                duration_ms=timeout * 1000,
                stderr=f"Test run timed out after {timeout} seconds."
            )
        except Exception as e:
            return TestRunResult(
                target=sanitized_target,
                exit_code=-1,
                success=False,
                stderr=f"Failed to launch test process: {str(e)}"
            )

diagnostics_engine = DiagnosticsEngine()
