import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_workflow_listing_and_defaults():
    res = client.get("/api/v1/workflows")
    assert res.status_code == 200
    workflows = res.json()
    assert len(workflows) >= 2
    names = [w["name"] for w in workflows]
    assert any("Telemetry" in n for n in names)
    assert any("Security" in n for n in names)


def test_workflow_execution_and_traces():
    # 1. Execute Default Telemetry Workflow
    exec_res = client.post("/api/v1/workflows/wf-telemetry-daily/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["status"] == "SUCCESS"
    assert data["duration_ms"] > 0
    assert len(data["traces"]) == 3
    assert data["traces"][0]["status"] == "SUCCESS"
    assert "Aggregated 4 nodes" in data["traces"][1]["output"]


def test_custom_workflow_crud_and_run():
    # 1. Create Workflow
    payload = {
        "name": "Custom Data Synthesis Pipeline",
        "description": "Transforms metrics and publishes to artifact studio",
        "trigger_type": "MANUAL",
        "nodes": [
            {"id": "n1", "name": "Start", "type": "TRIGGER", "config": {}},
            {"id": "n2", "name": "Compute Metric", "type": "CODE_SANDBOX", "config": {"language": "python", "code": "print('Metric=99.8')"}},
            {"id": "n3", "name": "Publish", "type": "OUTPUT", "config": {"format": "JSON"}},
        ],
        "edges": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
        ],
    }
    create_res = client.post("/api/v1/workflows", json=payload)
    assert create_res.status_code == 200
    wf = create_res.json()
    wf_id = wf["id"]
    assert wf["name"] == "Custom Data Synthesis Pipeline"
    assert len(wf["nodes"]) == 3

    # 2. Execute Custom Workflow
    run_res = client.post(f"/api/v1/workflows/{wf_id}/execute")
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "SUCCESS"
    assert len(run_data["traces"]) == 3
    assert "Metric=99.8" in run_data["traces"][1]["output"]

    # 3. Delete Workflow
    del_res = client.delete(f"/api/v1/workflows/{wf_id}")
    assert del_res.status_code == 200

    # 4. Verify 404
    get_res = client.get(f"/api/v1/workflows/{wf_id}")
    assert get_res.status_code == 404
