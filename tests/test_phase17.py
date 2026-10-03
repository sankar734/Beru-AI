import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_autopilot_suggestions_and_config():
    # 1. Config
    cfg_res = client.get("/api/v1/autopilot/config")
    assert cfg_res.status_code == 200
    cfg = cfg_res.json()
    assert cfg["mode"] == "FULL_AUTOPILOT"
    assert len(cfg["active_monitors"]) >= 2

    # 2. List Suggestions
    sug_res = client.get("/api/v1/autopilot/suggestions")
    assert sug_res.status_code == 200
    suggestions = sug_res.json()
    assert len(suggestions) >= 2
    assert any(s["category"] == "SECURITY" for s in suggestions)
    assert any(s["category"] == "PERFORMANCE" for s in suggestions)


def test_autopilot_apply_and_dismiss():
    # 1. Get initial suggestions
    sug_res = client.get("/api/v1/autopilot/suggestions")
    suggestions = sug_res.json()
    target_sug = suggestions[0]
    target_id = target_sug["id"]

    # 2. Apply Suggestion
    apply_res = client.post(f"/api/v1/autopilot/suggestions/{target_id}/apply")
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["status"] == "SUCCESS"
    assert apply_data["verification"]["verified"] is True

    # 3. Dismiss another suggestion
    remaining = [s for s in client.get("/api/v1/autopilot/suggestions").json() if s["id"] != target_id]
    if remaining:
        dismiss_id = remaining[0]["id"]
        dis_res = client.post(f"/api/v1/autopilot/suggestions/{dismiss_id}/dismiss")
        assert dis_res.status_code == 200

        # Verify dismissed
        current_list = client.get("/api/v1/autopilot/suggestions").json()
        assert not any(s["id"] == dismiss_id for s in current_list)
