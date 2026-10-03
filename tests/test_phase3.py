import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from services.ai_core.registry import provider_registry
from services.ai_core.router import intelligence_router, RouteRequest
from services.ai_core.provider_base import ChatMessagePayload, ChatRole

@pytest.mark.asyncio
async def test_provider_registry_and_mock():
    # 1. Check registry providers
    providers = provider_registry.list_providers()
    assert "mock" in providers
    assert "openai" in providers
    assert "anthropic" in providers
    assert "google" in providers
    assert "local" in providers

    # 2. Test MockProvider streaming
    mock = provider_registry.get_provider("mock")
    chunks = []
    async for chunk in mock.chat_stream([ChatMessagePayload(role=ChatRole.USER, content="Hello NOVA X")]):
        chunks.append(chunk)

    assert any(c.thought for c in chunks)
    assert any(c.token for c in chunks)
    assert chunks[-1].done is True

    # 3. Test MockProvider embeddings
    vectors = await mock.generate_embeddings(["Vector 1", "Vector 2"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 128

@pytest.mark.asyncio
async def test_intelligence_router_rules():
    # Rule: Code query -> Claude / code_specialist
    code_res = intelligence_router.route(RouteRequest(
        query="def optimize_async_loop(): pass",
        mode="AUTO"
    ))
    assert code_res.pipeline == "code_specialist"
    assert code_res.selected_provider == "anthropic"

    # Rule: Research mode -> o3-mini / deep_research_tree
    research_res = intelligence_router.route(RouteRequest(
        query="Exhaustive literature review on RAG",
        mode="RESEARCH"
    ))
    assert research_res.pipeline == "deep_research_tree"
    assert "search_web" in research_res.requires_tools

    # Rule: Privacy local_only -> Local / llama3
    priv_res = intelligence_router.route(RouteRequest(
        query="Analyze local secret key config",
        mode="AUTO",
        privacy_level="local_only"
    ))
    assert priv_res.selected_provider == "local"
    assert priv_res.pipeline == "local_offline"

    # Rule: Image attachment -> gpt-4o / vision_multimodal
    vision_res = intelligence_router.route(RouteRequest(
        query="Explain this error",
        has_attachments=True,
        attachment_types=["image/png"]
    ))
    assert vision_res.selected_provider == "openai"
    assert vision_res.pipeline == "vision_multimodal"

@pytest.mark.asyncio
async def test_models_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Providers endpoint
        prov_res = await client.get("/api/v1/models/providers")
        assert prov_res.status_code == 200
        data = prov_res.json()
        assert "mock" in data

        # Capabilities endpoint
        cap_res = await client.get("/api/v1/models/capabilities")
        assert cap_res.status_code == 200
        caps = cap_res.json()
        assert "CHAT" in caps
        assert "REASONING" in caps
        assert "EMBEDDINGS" in caps

        # Route endpoint
        route_res = await client.post("/api/v1/models/route", json={
            "query": "Who won the latest Nobel Prize?",
            "mode": "SEARCH"
        })
        assert route_res.status_code == 200
        route_data = route_res.json()
        assert route_data["pipeline"] == "grounded_search"
        assert route_data["selected_provider"] == "google"
