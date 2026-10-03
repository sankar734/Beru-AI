import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager

@pytest.mark.asyncio
async def test_deep_research_lifecycle():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register user
        auth_res = await client.post("/api/v1/auth/register", json={
            "email": "researcher@novax.local",
            "name": "Dr. Nova Researcher",
            "password": "ResearchPass777!"
        })
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Deep Research Job
        job_res = await client.post("/api/v1/research/jobs", json={
            "goal": "Autonomous Agent Safety and Verification Architectures",
            "depth": "comprehensive"
        }, headers=headers)
        assert job_res.status_code == 201
        job_data = job_res.json()
        job_id = job_data["id"]
        assert job_data["status"] == "COMPLETED"
        assert job_data["progress"] == 100
        assert len(job_data["subquestions"]) >= 3
        assert len(job_data["evidence"]) >= 3
        assert any(e["is_contradiction"] is True for e in job_data["evidence"])
        assert "DEEP RESEARCH REPORT" in job_data["final_report"]

        # 3. List research jobs
        list_res = await client.get("/api/v1/research/jobs", headers=headers)
        assert list_res.status_code == 200
        assert any(j["id"] == job_id for j in list_res.json())

        # 4. Get specific job
        get_res = await client.get(f"/api/v1/research/jobs/{job_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == job_id

        # 5. Test cancel endpoint
        cancel_res = await client.post(f"/api/v1/research/jobs/{job_id}/cancel", headers=headers)
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"
