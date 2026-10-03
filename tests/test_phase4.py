import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from services.ai_core.search.search_base import SearchCategory, SearchResultItem
from services.ai_core.search.mock_search import MockSearchProvider
from services.ai_core.search.citation_verifier import citation_verifier
from services.ai_core.search.search_pipeline import search_pipeline

@pytest.mark.asyncio
async def test_search_provider():
    provider = MockSearchProvider()
    results = await provider.search("Hybrid RAG architecture", SearchCategory.ACADEMIC)
    assert len(results) >= 2
    assert "rag" in results[0].snippet.lower() or "retrieval" in results[0].snippet.lower()
    assert results[0].score > 0.8

@pytest.mark.asyncio
async def test_citation_verifier():
    sources = [
        SearchResultItem(
            id="1",
            url="https://example.com/rag",
            title="State of RAG",
            snippet="Hybrid search combining lexical BM25 and semantic dense vectors with cross-encoders."
        )
    ]

    # Valid claim that exists in snippet
    valid_claim = "Combining lexical BM25 and semantic dense vectors"
    is_valid, score, src = citation_verifier.verify_citation(valid_claim, sources)
    assert is_valid is True
    assert score >= 0.4
    assert src.url == "https://example.com/rag"

    # Hallucinated / Fabricated claim that has 0 overlap
    fabricated_claim = "Flying penguins build quantum spaceships on Jupiter"
    is_invalid, zero_score, _ = citation_verifier.verify_citation(fabricated_claim, sources)
    assert is_invalid is False
    assert zero_score < 0.1

@pytest.mark.asyncio
async def test_search_pipeline_execution():
    res = await search_pipeline.execute("Hybrid RAG", SearchCategory.WEB)
    assert res.query == "Hybrid RAG"
    assert len(res.sources) >= 1
    assert len(res.citations) >= 1
    assert res.citations[0].verified is True
    assert "[1]" in res.answer

@pytest.mark.asyncio
async def test_search_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Categories endpoint
        cat_res = await client.get("/api/v1/search/categories")
        assert cat_res.status_code == 200
        cats = cat_res.json()
        assert "WEB" in cats
        assert "ACADEMIC" in cats

        # Search Query endpoint
        query_res = await client.post("/api/v1/search/query", json={
            "query": "Quantum RAG systems",
            "category": "WEB"
        })
        assert query_res.status_code == 200
        data = query_res.json()
        assert "answer" in data
        assert "citations" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
