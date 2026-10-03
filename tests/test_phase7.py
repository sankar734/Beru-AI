import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager

@pytest.mark.asyncio
async def test_projects_and_memory_lifecycle():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register user
        auth_res = await client.post("/api/v1/auth/register", json={
            "email": "pm@novax.local",
            "name": "Project Manager",
            "password": "ProjectManagerPass123!"
        })
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Project
        proj_res = await client.post("/api/v1/projects", json={
            "name": "EventSphere AI Integration",
            "description": "Full-stack project for event management and ticketing",
            "system_instructions": "Always respond concisely with TypeScript code.",
            "custom_rules": ["Use Tailwind CSS", "Enforce strict typing"]
        }, headers=headers)
        assert proj_res.status_code == 201
        proj_data = proj_res.json()
        proj_id = proj_data["id"]
        assert proj_data["name"] == "EventSphere AI Integration"

        # 3. List Projects
        list_proj = await client.get("/api/v1/projects", headers=headers)
        assert list_proj.status_code == 200
        assert any(p["id"] == proj_id for p in list_proj.json())

        # 4. Create Controlled Memory
        mem_res = await client.post("/api/v1/memory", json={
            "content": "User prefers concise Python 3.14 code with async/await patterns.",
            "memory_type": "PREFERENCE",
            "project_id": proj_id,
            "tags": ["python", "coding_style"]
        }, headers=headers)
        assert mem_res.status_code == 201
        mem_data = mem_res.json()
        mem_id = mem_data["id"]
        assert mem_data["is_active"] is True
        assert mem_data["memory_type"] == "PREFERENCE"

        # 5. List Memories
        mems_list = await client.get("/api/v1/memory", headers=headers)
        assert mems_list.status_code == 200
        assert any(m["id"] == mem_id for m in mems_list.json())

        # 6. Update Memory (Disable/Toggle)
        patch_mem = await client.patch(f"/api/v1/memory/{mem_id}", json={
            "is_active": False
        }, headers=headers)
        assert patch_mem.status_code == 200
        assert patch_mem.json()["is_active"] is False

        # 7. Knowledge Graph Relation
        graph_res = await client.post("/api/v1/memory/graph/relations", json={
            "id": "rel-1",
            "source_id": proj_id,
            "target_id": mem_id,
            "relation_type": "CONTAINS"
        }, headers=headers)
        assert graph_res.status_code == 200
        assert graph_res.json()["relation_type"] == "CONTAINS"

        # 8. Delete Memory
        del_mem = await client.delete(f"/api/v1/memory/{mem_id}", headers=headers)
        assert del_mem.status_code == 200

        # 9. Delete Project
        del_proj = await client.delete(f"/api/v1/projects/{proj_id}", headers=headers)
        assert del_proj.status_code == 200
