import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from services.code_runner.sandbox import sandbox_runner, CodeExecutionRequest

client = TestClient(app)


def test_sandbox_python_execution():
    req = CodeExecutionRequest(
        language="python",
        code="print('Hello from NOVA X Sandbox!')",
        timeout_seconds=5.0,
    )
    result = sandbox_runner.execute(req)
    assert result.status == "SUCCESS"
    assert "Hello from NOVA X Sandbox!" in result.stdout
    assert result.exit_code == 0
    assert result.duration_ms > 0


def test_sandbox_secret_redaction():
    code_with_secret = (
        "print('Secret is: sk-abcdef1234567890abcdef123456')\n"
    )
    req = CodeExecutionRequest(
        language="python",
        code=code_with_secret,
        timeout_seconds=5.0,
    )
    result = sandbox_runner.execute(req)
    assert result.status == "SUCCESS"
    assert "sk-abcdef1234567890abcdef123456" not in result.stdout
    assert "[REDACTED_SECRET]" in result.stdout


def test_sandbox_security_blocking():
    dangerous_code = "import os\nos.system('rm -rf /')\n"
    req = CodeExecutionRequest(
        language="python",
        code=dangerous_code,
        timeout_seconds=5.0,
    )
    result = sandbox_runner.execute(req)
    assert result.status == "BLOCKED"
    assert "Execution blocked by NOVA Security Policy" in result.stderr
    assert len(result.security_warnings) > 0


def test_sandbox_timeout_handling():
    infinite_loop = "import time\ntime.sleep(2.0)\nprint('Done')"
    req = CodeExecutionRequest(
        language="python",
        code=infinite_loop,
        timeout_seconds=0.6,
    )
    result = sandbox_runner.execute(req)
    assert result.status == "TIMEOUT"
    assert "timed out" in result.stderr


def test_code_api_endpoints():
    # 1. Execute
    res = client.post(
        "/api/v1/code/execute",
        json={"language": "python", "code": "print(2 + 2)", "timeout_seconds": 3.0},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "4" in data["stdout"].strip()

    # 2. Analyze
    res_an = client.post(
        "/api/v1/code/analyze",
        json={"code": "for i in range(10):\n    print(i)", "language": "python"},
    )
    assert res_an.status_code == 200
    an_data = res_an.json()
    assert an_data["is_safe"] is True
    assert an_data["line_count"] == 2

    # 3. Templates
    res_tmpl = client.get("/api/v1/code/templates")
    assert res_tmpl.status_code == 200
    tmpl_data = res_tmpl.json()
    assert "python" in tmpl_data["templates"]
