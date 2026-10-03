import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager

@pytest.mark.asyncio
async def test_auth_flow():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register a new user
        reg_payload = {
            "email": "agent@novax.local",
            "name": "Nova Operator",
            "password": "SuperSecretPassword123!"
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "agent@novax.local"
        assert data["user"]["name"] == "Nova Operator"
        token = data["access_token"]

        # 2. Try registering with duplicate email -> should fail 400
        dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_res.status_code == 400
        assert "already exists" in dup_res.json()["detail"]

        # 3. Access /api/v1/auth/me with valid token -> 200
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == "agent@novax.local"
        assert me_data["name"] == "Nova Operator"

        # 4. Access /api/v1/auth/me without token -> 401
        unauth_res = await client.get("/api/v1/auth/me")
        assert unauth_res.status_code == 401

        # 5. Access /api/v1/auth/me with invalid token -> 401
        bad_token_res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer badtoken"})
        assert bad_token_res.status_code == 401

        # 6. Login with correct password -> 200
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "agent@novax.local",
            "password": "SuperSecretPassword123!"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        assert login_data["user"]["email"] == "agent@novax.local"

        # 7. Login with wrong password -> 401
        wrong_pwd_res = await client.post("/api/v1/auth/login", json={
            "email": "agent@novax.local",
            "password": "WrongPassword!"
        })
        assert wrong_pwd_res.status_code == 401

        # 8. Logout endpoint with valid token -> 200
        logout_res = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_res.status_code == 200
        assert logout_res.json()["message"] == "Successfully logged out"
