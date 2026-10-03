import math
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VectorRecord(BaseModel):
    id: str
    vector: List[float]
    payload: Dict[str, Any]

class VectorQueryResult(BaseModel):
    id: str
    score: float
    payload: Dict[str, Any]

class BaseVectorStore(ABC):
    @abstractmethod
    async def upsert(self, collection_name: str, records: List[VectorRecord]):
        pass

    @abstractmethod
    async def query(
        self,
        collection_name: str,
        query_vector: List[float],
        filter_payload: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[VectorQueryResult]:
        pass

    @abstractmethod
    async def delete_by_file_id(self, collection_name: str, file_id: str):
        pass

class InMemoryVectorStore(BaseVectorStore):
    """In-memory cosine similarity vector database for fast, self-contained RAG."""
    def __init__(self):
        self._collections: Dict[str, List[VectorRecord]] = {}

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1)) or 1.0
        norm2 = math.sqrt(sum(b * b for b in v2)) or 1.0
        return dot / (norm1 * norm2)

    async def upsert(self, collection_name: str, records: List[VectorRecord]):
        if collection_name not in self._collections:
            self._collections[collection_name] = []
        
        # Remove existing with same IDs
        existing_ids = {r.id for r in records}
        self._collections[collection_name] = [
            r for r in self._collections[collection_name] if r.id not in existing_ids
        ]
        self._collections[collection_name].extend(records)

    async def query(
        self,
        collection_name: str,
        query_vector: List[float],
        filter_payload: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[VectorQueryResult]:
        records = self._collections.get(collection_name, [])
        scored_results: List[VectorQueryResult] = []

        for record in records:
            # Check filter matching
            if filter_payload:
                match = True
                for k, v in filter_payload.items():
                    if record.payload.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            sim = self._cosine_similarity(query_vector, record.vector)
            scored_results.append(VectorQueryResult(
                id=record.id,
                score=round(sim, 4),
                payload=record.payload
            ))

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]

    async def delete_by_file_id(self, collection_name: str, file_id: str):
        if collection_name in self._collections:
            self._collections[collection_name] = [
                r for r in self._collections[collection_name] if r.payload.get("file_id") != file_id
            ]

vector_store = InMemoryVectorStore()

def get_vector_store() -> BaseVectorStore:
    return vector_store
