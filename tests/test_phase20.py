import os
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_approved_roots():
    res = client.get("/api/v1/desktop/files/roots")
    assert res.status_code == 200
    roots = res.json()["allowed_roots"]
    assert len(roots) >= 1
    assert any("Beru" in r for r in roots)


def test_indexing_within_approved_root():
    root = os.path.abspath(r"d:\5536\Projects\Beru")
    res = client.post("/api/v1/desktop/files/index", json={"root_path": root, "max_files": 25})
    assert res.status_code == 200
    files = res.json()
    assert len(files) > 0
    first = files[0]
    assert first["filename"] != ""
    assert first["size_bytes"] >= 0
    assert first["extension"] != ""


def test_traversal_and_unauthorized_path_blocked():
    # Attempt unauthorized access to system root
    bad_res = client.post(
        "/api/v1/desktop/files/index",
        json={"root_path": r"c:\windows\system32", "max_files": 10},
    )
    assert bad_res.status_code == 403
    assert "ACCESS_DENIED" in bad_res.json()["detail"]


def test_local_file_search():
    root = os.path.abspath(r"d:\5536\Projects\Beru")
    res = client.get(f"/api/v1/desktop/files/search?query=FastAPI&root_path={root}&limit=5")
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) > 0
    assert any("py" in m["extension"] or "md" in m["extension"] for m in matches)
