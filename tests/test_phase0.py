import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.config import settings
from apps.api.database import db_manager
from apps.api.redis_client import redis_manager

@pytest.mark.asyncio
async def test_settings_loaded():
    assert settings.APP_NAME == "NOVA X"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.PORT == 8000

@pytest.mark.asyncio
async def test_database_crud():
    await db_manager.connect()
    coll = db_manager.get_collection("test_entities")
    # Insert
    res = await coll.insert_one({"name": "NovaTest", "val": 42})
    assert res.inserted_id is not None
    # Find
    item = await coll.find_one({"name": "NovaTest"})
    assert item is not None
    assert item["val"] == 42
    # Update
    up_res = await coll.update_one({"name": "NovaTest"}, {"$set": {"val": 100}})
    assert up_res.modified_count == 1
    updated_item = await coll.find_one({"name": "NovaTest"})
    assert updated_item["val"] == 100
    # Delete
    del_res = await coll.delete_one({"name": "NovaTest"})
    assert del_res.deleted_count == 1
    assert await coll.find_one({"name": "NovaTest"}) is None

@pytest.mark.asyncio
async def test_redis_client_operations():
    await redis_manager.connect()
    r = redis_manager.get_client()
    assert await r.set("test_key", "nova_val") is True
    assert await r.get("test_key") == "nova_val"
    assert await r.delete("test_key") == 1
    assert await r.get("test_key") is None

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "NOVA X"
        assert "x-request-id" in response.headers
        assert "x-process-time-ms" in response.headers

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NOVA X"
