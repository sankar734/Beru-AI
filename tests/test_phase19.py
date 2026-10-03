import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_window_enumeration_and_focus():
    # 1. Enumerate Windows
    res = client.get("/api/v1/desktop/windows")
    assert res.status_code == 200
    windows = res.json()
    assert len(windows) > 0
    first_win = windows[0]
    assert first_win["hwnd"] > 0
    assert first_win["title"] != ""
    assert first_win["pid"] > 0

    # 2. Focus Window
    focus_res = client.post(f"/api/v1/desktop/windows/{first_win['hwnd']}/focus")
    assert focus_res.status_code == 200
    assert focus_res.json()["status"] in ("success", "failed")

    # 3. Send Keys
    keys_res = client.post(
        f"/api/v1/desktop/windows/{first_win['hwnd']}/send-keys",
        json={"text": "NOVA_TEST"},
    )
    assert keys_res.status_code == 200
    assert keys_res.json()["injected_length"] == len("NOVA_TEST")
