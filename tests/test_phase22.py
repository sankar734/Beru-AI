import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_browser_navigation():
    res = client.post("/api/v1/browser/navigate", json={"url": "https://docs.python.org/3/"})
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == 200
    assert data["clean_text"] != ""
    assert isinstance(data["links"], list)
    assert data["duration_ms"] >= 0


def test_browser_ssrf_blocked():
    bad_res = client.post(
        "/api/v1/browser/navigate",
        json={"url": "http://169.254.169.254/latest/meta-data/"},
    )
    assert bad_res.status_code == 400
    assert "SECURITY_VIOLATION" in bad_res.json()["detail"]


def test_browser_forbidden_scheme_blocked():
    bad_res = client.post(
        "/api/v1/browser/navigate",
        json={"url": "file:///c:/windows/system32/cmd.exe"},
    )
    assert bad_res.status_code == 400
    assert "SECURITY_VIOLATION" in bad_res.json()["detail"]
