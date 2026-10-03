import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_voice_system_vitals_command():
    resp = client.post("/api/v1/voice/command", json={
        "command_text": "Hey NOVA, check system status please",
        "synthesize_response": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "SYSTEM_VITALS"
    assert data["risk_level"] == 0
    assert data["requires_confirmation"] is False
    assert data["status"] == "COMPLETED"
    assert "cpu_percent" in data["result"]
    assert data["audio_response_base64"] is not None

def test_voice_screen_capture_command():
    resp = client.post("/api/v1/voice/command", json={
        "command_text": "Please take a screenshot of my screen",
        "synthesize_response": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "SCREEN_CAPTURE"
    assert data["risk_level"] == 1
    assert data["status"] == "COMPLETED"
    assert data["result"]["has_image"] is True

def test_voice_window_focus_command():
    resp = client.post("/api/v1/voice/command", json={
        "command_text": "Switch to Chrome browser",
        "synthesize_response": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "WINDOW_FOCUS"
    assert data["params"]["title_query"] == "chrome browser"

def test_voice_app_launch_high_risk_and_confirmation_barrier():
    # 1. High risk command triggers AWAITING_CONFIRMATION
    resp = client.post("/api/v1/voice/command", json={
        "command_text": "Open notepad now",
        "synthesize_response": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "APP_LAUNCH"
    assert data["risk_level"] >= 3
    assert data["requires_confirmation"] is True
    assert data["status"] == "AWAITING_CONFIRMATION"
    action_id = data["action_id"]

    # 2. Reject action
    reject_resp = client.post("/api/v1/voice/confirm", json={
        "action_id": action_id,
        "confirmed": False
    })
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"

    # 3. Create another high risk command and approve it
    resp2 = client.post("/api/v1/voice/command", json={
        "command_text": "Launch notepad",
        "synthesize_response": True
    })
    action_id2 = resp2.json()["action_id"]

    approve_resp = client.post("/api/v1/voice/confirm", json={
        "action_id": action_id2,
        "confirmed": True
    })
    assert approve_resp.status_code == 200
    approve_data = approve_resp.json()
    assert approve_data["status"] == "CONFIRMED"
    assert approve_data["result"] is not None

def test_voice_history():
    resp = client.get("/api/v1/voice/history?limit=10")
    assert resp.status_code == 200
    history = resp.json()
    assert isinstance(history, list)
    assert len(history) > 0
