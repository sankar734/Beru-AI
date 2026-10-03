import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_tool_registry_introspection():
    res = client.get("/api/v1/tools")
    assert res.status_code == 200
    tools = res.json()["tools"]
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "file_read" in tool_names
    assert "file_write" in tool_names
    assert "file_delete" in tool_names
    assert "code_sandbox_run" in tool_names


def test_level_0_calculator_execution():
    # 1. Propose Level 0
    prop_res = client.post("/api/v1/tools/propose", json={"tool_name": "calculator", "params": {"expression": "(15 * 4) + 10"}})
    assert prop_res.status_code == 200
    prop = prop_res.json()
    assert prop["risk_level"] == 0
    assert prop["requires_approval"] is False

    # 2. Execute Level 0 directly
    exec_res = client.post("/api/v1/tools/execute", json={"tool_name": "calculator", "params": {"expression": "(15 * 4) + 10"}})
    assert exec_res.status_code == 200
    result = exec_res.json()
    assert result["success"] is True
    assert result["output"] == 70
    assert result["verification"]["verified"] is True


def test_level_3_policy_barrier_and_verified_file_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_out.txt")
        test_content = "Verified NOVA X System State Assertion"

        # 1. Unapproved attempt MUST be blocked
        blocked_res = client.post(
            "/api/v1/tools/execute",
            json={"tool_name": "file_write", "params": {"filepath": test_file, "content": test_content}},
        )
        assert blocked_res.status_code == 200
        blocked_data = blocked_res.json()
        assert blocked_data["success"] is False
        assert "SECURITY_VIOLATION" in blocked_data["error"]
        assert not os.path.exists(test_file)

        # 2. Propose Action
        prop_res = client.post(
            "/api/v1/tools/propose",
            json={"tool_name": "file_write", "params": {"filepath": test_file, "content": test_content}},
        )
        assert prop_res.status_code == 200
        prop = prop_res.json()
        assert prop["risk_level"] == 3
        assert prop["requires_approval"] is True
        request_id = prop["approval_request"]["request_id"]

        # 3. User Approves Action
        appr_res = client.post("/api/v1/tools/approve", json={"request_id": request_id, "approved": True})
        assert appr_res.status_code == 200
        approval = appr_res.json()
        assert approval["status"] == "APPROVED"
        token = approval["approval_token"]
        assert token is not None

        # 4. Execute with Valid Token
        exec_res = client.post(
            "/api/v1/tools/execute",
            json={
                "tool_name": "file_write",
                "params": {"filepath": test_file, "content": test_content},
                "approval_token": token,
            },
        )
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        assert exec_data["success"] is True
        assert exec_data["verification"]["verified"] is True
        assert os.path.exists(test_file)

        # Verify disk state
        with open(test_file, "r", encoding="utf-8") as f:
            assert f.read() == test_content


def test_level_4_policy_barrier_and_verified_file_delete():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "to_delete.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("temporary file")

        # 1. Propose Deletion (Risk Level 4)
        prop_res = client.post(
            "/api/v1/tools/propose",
            json={"tool_name": "file_delete", "params": {"filepath": test_file}},
        )
        assert prop_res.status_code == 200
        prop = prop_res.json()
        assert prop["risk_level"] == 4
        assert prop["requires_approval"] is True
        req_id = prop["approval_request"]["request_id"]

        # 2. Approve
        appr_res = client.post("/api/v1/tools/approve", json={"request_id": req_id, "approved": True})
        token = appr_res.json()["approval_token"]

        # 3. Execute and verify absence
        exec_res = client.post(
            "/api/v1/tools/execute",
            json={"tool_name": "file_delete", "params": {"filepath": test_file}, "approval_token": token},
        )
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        assert exec_data["success"] is True
        assert exec_data["verification"]["verified"] is True
        assert not os.path.exists(test_file)
