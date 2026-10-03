import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_tasks_and_goals_defaults():
    # 1. Goals
    g_res = client.get("/api/v1/tasks/goals")
    assert g_res.status_code == 200
    goals = g_res.json()
    assert len(goals) >= 1
    assert "NOVA X" in goals[0]["title"]

    # 2. Tasks
    t_res = client.get("/api/v1/tasks")
    assert t_res.status_code == 200
    tasks = t_res.json()
    assert len(tasks) >= 3


def test_task_lifecycle_and_agent_dispatch():
    # 1. Create Task
    create_payload = {
        "title": "Automated security validation pass",
        "description": "Run security inspection checks across modules",
        "priority": "HIGH",
    }
    create_res = client.post("/api/v1/tasks", json=create_payload)
    assert create_res.status_code == 200
    task = create_res.json()
    task_id = task["id"]
    assert task["status"] == "TODO"
    assert task["priority"] == "HIGH"

    # 2. Dispatch Agent for Task
    disp_res = client.post(f"/api/v1/tasks/{task_id}/dispatch-agent")
    assert disp_res.status_code == 200
    disp_data = disp_res.json()
    assert disp_data["task_id"] == task_id
    assert disp_data["agent_run_id"] is not None

    # 3. Verify Task was updated with assigned_agent_id
    get_res = client.get("/api/v1/tasks")
    tasks = get_res.json()
    updated_task = next(t for t in tasks if t["id"] == task_id)
    assert updated_task["assigned_agent_id"] == disp_data["agent_run_id"]
    assert updated_task["status"] in ("IN_PROGRESS", "COMPLETED")

    # 4. Delete Task
    del_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 200
