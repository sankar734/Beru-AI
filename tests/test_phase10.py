import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_artifact_crud_and_versioning():
    # 1. Create Artifact
    create_payload = {
        "title": "Interactive Physics Simulator",
        "type": "WEB_APP",
        "description": "2D canvas simulation of gravitational fields",
        "initial_content": "<html><body><h1>Simulation v1</h1></body></html>",
        "tags": ["physics", "simulation"],
    }
    create_res = client.post("/api/v1/artifacts", json=create_payload)
    assert create_res.status_code == 200
    art = create_res.json()
    art_id = art["id"]
    assert art["title"] == "Interactive Physics Simulator"
    assert art["current_version"] == 1
    assert len(art["versions"]) == 1
    assert "Simulation v1" in art["versions"][0]["content"]

    # 2. Update with new version snapshot
    update_payload = {
        "new_content": "<html><body><h1>Simulation v2 - Added Collision Dynamics</h1></body></html>",
        "version_summary": "Added particle collisions",
    }
    update_res = client.put(f"/api/v1/artifacts/{art_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_art = update_res.json()
    assert updated_art["current_version"] == 2
    assert len(updated_art["versions"]) == 2

    # 3. Compute Diff
    diff_res = client.get(f"/api/v1/artifacts/{art_id}/diff?v1=1&v2=2")
    assert diff_res.status_code == 200
    diff_data = diff_res.json()
    assert diff_data["has_changes"] is True
    assert any("Simulation v2" in line for line in diff_data["diff_lines"])

    # 4. List and filter
    list_res = client.get("/api/v1/artifacts?type=WEB_APP")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["id"] == art_id for item in items)

    # 5. Delete Artifact
    del_res = client.delete(f"/api/v1/artifacts/{art_id}")
    assert del_res.status_code == 200

    # 6. Verify 404 after deletion
    get_res = client.get(f"/api/v1/artifacts/{art_id}")
    assert get_res.status_code == 404
