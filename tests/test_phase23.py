import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.routers.auth import create_access_token
from services.developer.supervisor import dev_supervisor
from services.developer.repo_service import RepoService
from services.developer.diagnostics import diagnostics_engine

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "user_dev_test", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_developer_services_and_restart(auth_headers):
    # 1. List services
    resp = client.get("/api/v1/developer/services", headers=auth_headers)
    assert resp.status_code == 200
    services = resp.json()
    assert len(services) >= 3
    service_ids = [s["id"] for s in services]
    assert "web-client" in service_ids
    assert "api-gateway" in service_ids

    # 2. Restart a service
    resp_restart = client.post("/api/v1/developer/services/api-gateway/restart", headers=auth_headers)
    assert resp_restart.status_code == 200
    data = resp_restart.json()
    assert data["status"] == "ONLINE"
    assert data["restarts_count"] >= 1

    # 3. View logs
    resp_logs = client.get("/api/v1/developer/services/api-gateway/logs", headers=auth_headers)
    assert resp_logs.status_code == 200
    logs = resp_logs.json().get("logs", [])
    assert len(logs) > 0
    assert any("restart" in line.lower() for line in logs)

def test_git_status_and_diff(auth_headers):
    # Git status
    resp = client.get("/api/v1/developer/git/status", headers=auth_headers)
    assert resp.status_code == 200
    git_info = resp.json()
    assert "branch" in git_info
    assert "workspace_root" in git_info

    # Diff calculation
    orig = "def add(a, b):\n    return a + b\n"
    modified = "def add(a, b):\n    # docstring\n    return a + b\n"
    diff_resp = client.post("/api/v1/developer/diff", headers=auth_headers, json={
        "original_text": orig,
        "new_text": modified,
        "filename": "calc.py"
    })
    assert diff_resp.status_code == 200
    diff_data = diff_resp.json()
    assert diff_data["additions"] == 1
    assert diff_data["deletions"] == 0
    assert "+    # docstring" in diff_data["diff"]

def test_multi_file_proposal_and_rollback():
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_svc = RepoService(workspace_root=tmp_dir)

        test_file = "service.py"
        full_path = os.path.join(tmp_dir, test_file)
        with open(full_path, "w") as f:
            f.write("def original_func():\n    return 42\n")

        # 1. Propose edit
        proposal = repo_svc.stage_edit_proposal(
            title="Update Function",
            description="Refactor to return 100",
            files_changes=[{"filepath": test_file, "new_content": "def original_func():\n    return 100\n"}]
        )
        assert proposal.status == "PENDING"
        assert len(proposal.changes) == 1
        assert proposal.changes[0].syntax_valid is True

        # 2. Apply proposal (Risk Level 2 -> can apply directly)
        apply_res = repo_svc.apply_proposal(proposal.proposal_id, human_approved=False)
        assert apply_res["success"] is True
        with open(full_path, "r") as f:
            assert f.read() == "def original_func():\n    return 100\n"

        # 3. Rollback proposal
        rollback_res = repo_svc.rollback_proposal(proposal.proposal_id)
        assert rollback_res["success"] is True
        with open(full_path, "r") as f:
            assert f.read() == "def original_func():\n    return 42\n"

def test_syntax_error_detection_and_high_risk_barrier():
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_svc = RepoService(workspace_root=tmp_dir)

        # Propose invalid python syntax
        proposal = repo_svc.stage_edit_proposal(
            title="Broken Code",
            description="Invalid syntax test",
            files_changes=[{"filepath": "broken.py", "new_content": "def invalid(\n"}]
        )
        assert proposal.changes[0].syntax_valid is False
        assert "SyntaxError" in proposal.changes[0].syntax_error

        # Propose critical file edit (main.py -> Risk Level 3)
        crit_proposal = repo_svc.stage_edit_proposal(
            title="Core Update",
            description="Touch main.py",
            files_changes=[{"filepath": "main.py", "new_content": "# core change\n"}]
        )
        assert crit_proposal.risk_level >= 3
        # Attempt apply without human approval
        blocked_res = repo_svc.apply_proposal(crit_proposal.proposal_id, human_approved=False)
        assert blocked_res["success"] is False
        assert blocked_res["status"] == "AWAITING_APPROVAL"

        # Apply with human approval
        approved_res = repo_svc.apply_proposal(crit_proposal.proposal_id, human_approved=True)
        assert approved_res["success"] is True

def test_traceback_diagnostics(auth_headers):
    traceback_sample = """
Traceback (most recent call last):
  File "apps/api/routers/demo.py", line 42, in handle_request
    result = 10 / 0
ZeroDivisionError: division by zero
"""
    resp = client.post("/api/v1/developer/diagnose", headers=auth_headers, json={"log_text": traceback_sample})
    assert resp.status_code == 200
    diag = resp.json()
    assert diag["has_error"] is True
    assert diag["error_type"] == "ZeroDivisionError"
    assert diag["target_file"] == "apps/api/routers/demo.py"
    assert diag["target_line"] == 42
    assert len(diag["remediation_steps"]) > 0

def test_sandboxed_test_runner(auth_headers):
    resp = client.post("/api/v1/developer/run-tests", headers=auth_headers, json={
        "test_target": "tests/test_phase0.py",
        "timeout": 15
    })
    assert resp.status_code == 200
    test_run = resp.json()
    assert test_run["success"] is True
    assert test_run["exit_code"] == 0
    assert test_run["passed_count"] >= 1
