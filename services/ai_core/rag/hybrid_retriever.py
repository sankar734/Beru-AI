import math
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from services.ai_core.rag.vector_store import BaseVectorStore, VectorQueryResult, get_vector_store
from services.ai_core.registry import get_provider_registry

class GroundedChunk(BaseModel):
    chunk_id: str
    file_id: str
    file_name: str
    page_number: int
    section_title: str
    text: str
    score: float

class HybridRetriever:
    def __init__(self, vector_store: Optional[BaseVectorStore] = None):
        self.vector_store = vector_store or get_vector_store()
        self.provider_registry = get_provider_registry()

    def _lexical_bm25_score(self, query_tokens: set, text: str) -> float:
        text_tokens = re.findall(r"\w+", text.lower())
        if not text_tokens:
            return 0.0
        
        matches = sum(1 for t in text_tokens if t in query_tokens)
        return matches / (len(text_tokens) ** 0.5)

    async def retrieve(
        self,
        query: str,
        collection_name: str = "nova_rag_chunks",
        filter_payload: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[GroundedChunk]:
        # 1. Generate query embedding
        provider = self.provider_registry.get_provider("mock")
        query_vectors = await provider.generate_embeddings([query])
        query_vector = query_vectors[0]

        # 2. Dense Semantic Search (retrieve top 15 candidates)
        dense_results = await self.vector_store.query(
            collection_name=collection_name,
            query_vector=query_vector,
            filter_payload=filter_payload,
            top_k=15
        )

        if not dense_results:
            return []

        # 3. Sparse Lexical Scoring
        query_tokens = set(re.findall(r"\w+", query.lower()))
        
        dense_ranks = {r.id: rank for rank, r in enumerate(dense_results)}
        
        lexical_scores = []
        for r in dense_results:
            text = r.payload.get("text", "")
            lex_score = self._lexical_bm25_score(query_tokens, text)
            lexical_scores.append((r.id, lex_score))
        
        lexical_scores.sort(key=lambda x: x[1], reverse=True)
        lexical_ranks = {item[0]: rank for rank, item in enumerate(lexical_scores)}

        # 4. Reciprocal Rank Fusion (RRF)
        # RRF_Score = 1 / (60 + dense_rank) + 1 / (60 + lexical_rank)
        rrf_scores: Dict[str, float] = {}
        for r in dense_results:
            r_id = r.id
            d_rank = dense_ranks.get(r_id, 100)
            l_rank = lexical_ranks.get(r_id, 100)
            score = (1.0 / (60.0 + d_rank)) + (1.0 / (60.0 + l_rank))
            rrf_scores[r_id] = score

        # Sort by combined RRF score
        dense_results.sort(key=lambda r: rrf_scores.get(r.id, 0.0), reverse=True)

        final_chunks: List[GroundedChunk] = []
        for r in dense_results[:top_k]:
            payload = r.payload
            final_chunks.append(GroundedChunk(
                chunk_id=r.id,
                file_id=payload.get("file_id", "unknown"),
                file_name=payload.get("file_name", "unknown.txt"),
                page_number=payload.get("page_number", 1),
                section_title=payload.get("section_title", "General"),
                text=payload.get("text", ""),
                score=round(rrf_scores.get(r.id, 0.0), 4)
            ))

        return final_chunks

hybrid_retriever = HybridRetriever()

def get_hybrid_retriever() -> HybridRetriever:
    return hybrid_retriever
