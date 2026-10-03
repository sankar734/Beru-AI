import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_desktop_system_vitals():
    res = client.get("/api/v1/desktop/status")
    assert res.status_code == 200
    vitals = res.json()
    assert vitals["os_name"] != ""
    assert vitals["cpu_cores"] > 0
    assert vitals["ram_total_gb"] > 0
    assert vitals["bridge_status"] == "CONNECTED"


def test_desktop_running_processes():
    res = client.get("/api/v1/desktop/processes?limit=5")
    assert res.status_code == 200
    procs = res.json()
    assert len(procs) > 0
    assert procs[0]["pid"] > 0
    assert procs[0]["name"] != ""
    assert procs[0]["memory_mb"] >= 0


def test_desktop_app_whitelist_and_security_barrier():
    # 1. Whitelist introspection
    list_res = client.get("/api/v1/desktop/apps")
    assert list_res.status_code == 200
    whitelist = list_res.json()["whitelist"]
    assert "notepad" in whitelist
    assert "calc" in whitelist

    # 2. Blocked forbidden application
    bad_res = client.post("/api/v1/desktop/launch-app", json={"app_key": "malicious_trojan.exe"})
    assert bad_res.status_code == 400
    assert "not permitted" in bad_res.json()["detail"]


def test_desktop_clipboard_operations():
    # 1. Write
    test_text = "NOVA X Zero-Trust Clipboard Token"
    write_res = client.post("/api/v1/desktop/clipboard", json={"text": test_text})
    assert write_res.status_code == 200
    assert write_res.json()["status"] == "success"

    # 2. Read
    read_res = client.get("/api/v1/desktop/clipboard")
    assert read_res.status_code == 200
    assert read_res.json()["clipboard"] == test_text
