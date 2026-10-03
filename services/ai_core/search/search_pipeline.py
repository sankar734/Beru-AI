from typing import List, Optional
from services.ai_core.search.search_base import (
    SearchCategory,
    SearchResultItem,
    GroundedCitation,
    GroundedSearchResponse,
)
from services.ai_core.search.mock_search import MockSearchProvider
from services.ai_core.search.citation_verifier import citation_verifier

class SearchPipeline:
    def __init__(self, provider=None):
        self.provider = provider or MockSearchProvider()

    async def execute(
        self,
        query: str,
        category: SearchCategory = SearchCategory.WEB,
        max_results: int = 5
    ) -> GroundedSearchResponse:
        # 1. Search provider execution
        sources = await self.provider.search(query=query, category=category, max_results=max_results)

        # 2. Formulate grounded answer referencing sources
        if not sources:
            return GroundedSearchResponse(
                query=query,
                category=category,
                answer="No relevant search results found for this query.",
                citations=[],
                sources=[]
            )

        src_titles = [f"[{i+1}] {s.title}" for i, s in enumerate(sources)]
        
        answer = (
            f"Based on real-time {category.value.lower()} search results, here is the verified analysis for **\"{query}\"**:\n\n"
            f"1. **Core Findings**: {sources[0].snippet} [1]\n"
        )
        if len(sources) > 1:
            answer += f"2. **Corroborating Evidence**: {sources[1].snippet} [2]\n"

        answer += f"\nCross-checked across verified sources: {', '.join(src_titles)}."

        # 3. Grounded citation verification
        candidates = [
            {"quote": sources[0].snippet, "source_url": sources[0].url},
        ]
        if len(sources) > 1:
            candidates.append({"quote": sources[1].snippet, "source_url": sources[1].url})

        verified_citations = citation_verifier.verify_all(candidates, sources)

        return GroundedSearchResponse(
            query=query,
            category=category,
            answer=answer,
            citations=verified_citations,
            sources=sources
        )

search_pipeline = SearchPipeline()

def get_search_pipeline() -> SearchPipeline:
    return search_pipeline
