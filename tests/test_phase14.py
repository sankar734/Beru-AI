import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_agent_launch_and_approval_barrier_pause():
    # 1. Launch Mission
    launch_payload = {
        "goal": "Audit codebase security and build verification",
        "mode": "AUTONOMOUS",
        "max_steps": 8,
    }
    launch_res = client.post("/api/v1/agents/run", json=launch_payload)
    assert launch_res.status_code == 200
    run = launch_res.json()
    run_id = run["id"]

    # Must be paused at AWAITING_APPROVAL because step 3 is file_write (Risk Level 3)
    assert run["status"] == "AWAITING_APPROVAL"
    assert run["pending_approval_id"] is not None
    assert len(run["steps"]) >= 3

    # Step 1 (Risk 0) must be completed
    assert run["steps"][0]["status"] == "COMPLETED"
    # Step 2 (Risk 2) must be completed
    assert run["steps"][1]["status"] == "COMPLETED"
    # Step 3 (Risk 3) must be awaiting approval
    assert run["steps"][2]["status"] == "AWAITING_APPROVAL"


def test_agent_approval_rejection():
    # 1. Launch Mission
    launch_res = client.post(
        "/api/v1/agents/run",
        json={"goal": "Verify numerical statistics", "mode": "AUTONOMOUS"},
    )
    assert launch_res.status_code == 200
    run = launch_res.json()
    run_id = run["id"]
    assert run["status"] == "AWAITING_APPROVAL"

    # 2. Reject Approval
    decide_res = client.post(f"/api/v1/agents/runs/{run_id}/approve", json={"approved": False})
    assert decide_res.status_code == 200
    resumed_run = decide_res.json()
    assert resumed_run["status"] == "STOPPED"
    assert "aborted" in resumed_run["final_summary"].lower()


def test_agent_approval_acceptance_and_completion():
    # 1. Launch Mission
    launch_res = client.post(
        "/api/v1/agents/run",
        json={"goal": "General system test execution", "mode": "AUTONOMOUS"},
    )
    assert launch_res.status_code == 200
    run = launch_res.json()
    run_id = run["id"]
    assert run["status"] == "AWAITING_APPROVAL"

    # 2. Accept Approval
    decide_res = client.post(f"/api/v1/agents/runs/{run_id}/approve", json={"approved": True})
    assert decide_res.status_code == 200
    completed_run = decide_res.json()
    assert completed_run["status"] == "COMPLETED"
    assert completed_run["current_step"] == len(completed_run["steps"])
    assert completed_run["steps"][2]["status"] == "COMPLETED"
    assert completed_run["steps"][2]["verification"]["verified"] is True
    assert "successfully executed" in completed_run["final_summary"]
