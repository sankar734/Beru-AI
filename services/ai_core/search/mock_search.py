import uuid
from typing import List
from services.ai_core.search.search_base import BaseSearchProvider, SearchCategory, SearchResultItem

class MockSearchProvider(BaseSearchProvider):
    def __init__(self):
        super().__init__("mock_search")

    async def search(
        self,
        query: str,
        category: SearchCategory = SearchCategory.WEB,
        max_results: int = 5
    ) -> List[SearchResultItem]:
        q_clean = query.strip()
        
        # Deterministic grounded search results based on query keywords
        if "rag" in q_clean.lower():
            return [
                SearchResultItem(
                    id="res-1",
                    url="https://arxiv.org/abs/2005.11401",
                    title="Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
                    snippet="We explore RAG models which combine pre-trained parametric and non-parametric memory for generation, yielding state-of-the-art results on open-domain QA.",
                    category=category,
                    score=0.98,
                    published_date="2020-05-22"
                ),
                SearchResultItem(
                    id="res-2",
                    url="https://docs.anthropic.com/en/docs/build-with-claude/rag",
                    title="Best Practices for Retrieval Augmented Generation | Claude Documentation",
                    snippet="Hybrid search combining lexical BM25 and semantic vector embeddings with cross-encoder rerankers dramatically improves retrieval recall.",
                    category=category,
                    score=0.95,
                    published_date="2024-08-10"
                )
            ]

        return [
            SearchResultItem(
                id="res-default-1",
                url=f"https://en.wikipedia.org/wiki/{q_clean.replace(' ', '_')}",
                title=f"{q_clean.capitalize()} - Encyclopedia Overview",
                snippet=f"{q_clean} is an established concept with widespread practical applications across computing, science, and engineering.",
                category=category,
                score=0.92,
                published_date="2024-01-15"
            ),
            SearchResultItem(
                id="res-default-2",
                url="https://docs.novax.local/intelligence-operating-system",
                title="NOVA X Systems & Policy Verification Architecture",
                snippet="NOVA X decouples intelligence from execution through an enforced policy engine and host verification engine.",
                category=category,
                score=0.89,
                published_date="2026-10-01"
            )
        ]
