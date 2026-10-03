import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager

@pytest.mark.asyncio
async def test_universal_chat_flow():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register user & obtain auth token
        auth_res = await client.post("/api/v1/auth/register", json={
            "email": "chatuser@novax.local",
            "name": "Chat Master",
            "password": "SecurePassword999!"
        })
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create conversation
        conv_res = await client.post("/api/v1/chat/conversations", json={
            "title": "Quantum Computing & RAG",
            "mode": "RESEARCH"
        }, headers=headers)
        assert conv_res.status_code == 201
        conv_data = conv_res.json()
        conv_id = conv_data["id"]
        assert conv_data["title"] == "Quantum Computing & RAG"
        assert conv_data["mode"] == "RESEARCH"

        # 3. List conversations
        list_res = await client.get("/api/v1/chat/conversations", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # 4. Send a message (JSON mode)
        msg_res = await client.post(f"/api/v1/chat/conversations/{conv_id}/messages", json={
            "content": "Explain hybrid RAG architecture and citations verification.",
            "mode": "RESEARCH"
        }, headers=headers)
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        assert "user_message" in msg_data
        assert "assistant_message" in msg_data
        asst_msg = msg_data["assistant_message"]
        assert len(asst_msg["citations"]) >= 1
        user_msg_id = msg_data["user_message"]["id"]

        # 5. Send message with SSE streaming (stream=true)
        stream_res = await client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages?stream=true",
            json={"content": "Stream me the verification rules", "mode": "AUTO"},
            headers=headers
        )
        assert stream_res.status_code == 200
        assert "text/event-stream" in stream_res.headers["content-type"]
        stream_body = stream_res.text
        assert "event: token" in stream_body
        assert "event: done" in stream_body

        # 6. Branch conversation from the first message
        branch_res = await client.post(
            f"/api/v1/chat/conversations/{conv_id}/branch?from_message_id={user_msg_id}",
            headers=headers
        )
        assert branch_res.status_code == 200
        branched_data = branch_res.json()
        assert "(Branch)" in branched_data["title"]
        assert len(branched_data["messages"]) == 1

        # 7. Update conversation (Pin and Rename)
        update_res = await client.patch(f"/api/v1/chat/conversations/{conv_id}", json={
            "title": "Renamed Quantum RAG",
            "pinned": True
        }, headers=headers)
        assert update_res.status_code == 200
        assert update_res.json()["pinned"] is True
        assert update_res.json()["title"] == "Renamed Quantum RAG"

        # 8. Delete conversation
        del_res = await client.delete(f"/api/v1/chat/conversations/{conv_id}", headers=headers)
        assert del_res.status_code == 200

        # Verify not found
        get_res = await client.get(f"/api/v1/chat/conversations/{conv_id}", headers=headers)
        assert get_res.status_code == 404
