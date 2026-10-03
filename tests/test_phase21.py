import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_screen_capture_endpoint():
    res = client.post("/api/v1/desktop/screen/capture")
    assert res.status_code == 200
    data = res.json()
    assert data["image_base64"] != ""
    assert data["width"] > 0
    assert data["height"] > 0
    assert data["secrets_sanitized"] is True


def test_screen_analyze_endpoint():
    res = client.post("/api/v1/desktop/screen/analyze", json={})
    assert res.status_code == 200
    analysis = res.json()
    assert analysis["analysis"] != ""
    assert isinstance(analysis["detected_labels"], list)
    assert analysis["detected_text"] is not None
    assert analysis["confidence"] > 0.0
