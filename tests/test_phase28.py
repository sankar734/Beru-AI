import os
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_production_deployment_artifacts_exist():
    workspace_root = os.getcwd()

    required_files = [
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "apps/api/Dockerfile",
        "apps/web/Dockerfile",
        "docker/nginx.conf",
        ".env.example",
        "README.md",
        "docs/architecture.md"
    ]

    for rel_path in required_files:
        full_path = os.path.join(workspace_root, rel_path)
        assert os.path.exists(full_path), f"Missing deployment file: {rel_path}"
        assert os.path.getsize(full_path) > 50, f"File {rel_path} appears empty or truncated"

def test_all_api_subsystems_mounted_and_reachable():
    endpoints = [
        ("/", 200),
        ("/api/v1/health", 200),
        ("/api/v1/models/providers", 200),
        ("/api/v1/tools", 200),
        ("/api/v1/agents/runs", 200),
        ("/api/v1/workflows", 200),
        ("/api/v1/tasks", 200),
        ("/api/v1/autopilot/suggestions", 200),
        ("/api/v1/desktop/status", 200),
        ("/api/v1/developer/services", 200),
        ("/api/v1/voice/history", 200),
        ("/api/v1/mcp/servers", 200),
        ("/api/v1/mcp/tools", 200),
        ("/api/v1/security/audit-trail", 200),
        ("/metrics", 200),
    ]

    for path, expected_status in endpoints:
        resp = client.get(path)
        assert resp.status_code == expected_status, f"Failed route {path}: got {resp.status_code}, expected {expected_status}"

def test_root_metadata_conforms_to_nova_x_spec():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "NOVA X"
    assert data["tagline"] == "Think. Search. Research. Create. Code. Learn. Act."
    assert data["version"] == "1.0.0"
