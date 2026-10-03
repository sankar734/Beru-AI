import io
import os
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager
from services.ai_core.rag.extractor import document_extractor
from services.ai_core.rag.chunker import text_chunker
from services.ai_core.rag.vector_store import get_vector_store, VectorRecord
from services.ai_core.rag.hybrid_retriever import hybrid_retriever

@pytest.mark.asyncio
async def test_text_chunker():
    sample_text = (
        "# Introduction to RAG\n"
        "Retrieval-Augmented Generation enhances LLM responses using external knowledge.\n\n"
        "--- Page 2 ---\n"
        "## Vector Embeddings\n"
        "Dense vectors capture deep semantic relationships between concepts across documents."
    )
    chunks = text_chunker.chunk_text(sample_text)
    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2
    assert chunks[0].word_count > 0

@pytest.mark.asyncio
async def test_vector_store_cosine():
    vstore = get_vector_store()
    records = [
        VectorRecord(id="v1", vector=[1.0, 0.0, 0.0], payload={"file_id": "f1", "tag": "ai"}),
        VectorRecord(id="v2", vector=[0.0, 1.0, 0.0], payload={"file_id": "f2", "tag": "bio"}),
    ]
    await vstore.upsert("test_vcol", records)

    # Query vector close to v1
    results = await vstore.query("test_vcol", query_vector=[0.9, 0.1, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0].id == "v1"
    assert results[0].score > 0.85

    # Query with filter
    bio_results = await vstore.query("test_vcol", query_vector=[1.0, 0.0, 0.0], filter_payload={"tag": "bio"}, top_k=1)
    assert len(bio_results) == 1
    assert bio_results[0].id == "v2"

@pytest.mark.asyncio
async def test_files_upload_and_rag_endpoints():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login/Register user
        auth_res = await client.post("/api/v1/auth/register", json={
            "email": "raguser@novax.local",
            "name": "RAG Specialist",
            "password": "RAGSecurePassword123!"
        })
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload file
        file_content = (
            "# NOVA X Architecture Specification\n"
            "NOVA X implements a zero-trust host security model where all desktop mutations "
            "require HMAC signatures and explicit user confirmation for Level 3 and 4 actions."
        )
        files = {
            "file": ("spec.md", io.BytesIO(file_content.encode("utf-8")), "text/markdown")
        }
        upload_res = await client.post("/api/v1/files/upload", files=files, headers=headers)
        assert upload_res.status_code == 201
        file_data = upload_res.json()
        file_id = file_data["id"]
        assert file_data["file_name"] == "spec.md"
        assert file_data["chunk_count"] >= 1

        # 3. List files
        list_res = await client.get("/api/v1/files", headers=headers)
        assert list_res.status_code == 200
        assert any(f["id"] == file_id for f in list_res.json())

        # 4. RAG Query against uploaded document
        rag_res = await client.post("/api/v1/files/rag/query", json={
            "query": "zero-trust host security model"
        }, headers=headers)
        assert rag_res.status_code == 200
        rag_data = rag_res.json()
        assert len(rag_data["grounded_chunks"]) >= 1
        assert rag_data["grounded_chunks"][0]["file_name"] == "spec.md"
        assert "[1]" in rag_data["answer"]

        # 5. Delete file
        del_res = await client.delete(f"/api/v1/files/{file_id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["id"] == file_id

        # Verify list no longer contains file
        list_res_after = await client.get("/api/v1/files", headers=headers)
        assert not any(f["id"] == file_id for f in list_res_after.json())
