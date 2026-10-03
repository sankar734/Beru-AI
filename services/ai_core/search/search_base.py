from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class SearchCategory(str, Enum):
    WEB = "WEB"
    NEWS = "NEWS"
    ACADEMIC = "ACADEMIC"
    DOCUMENTATION = "DOCUMENTATION"

class SearchResultItem(BaseModel):
    id: str
    url: str
    title: str
    snippet: str
    category: SearchCategory = SearchCategory.WEB
    score: float = 1.0
    published_date: Optional[str] = None

class GroundedCitation(BaseModel):
    citation_id: int
    source_url: str
    source_title: str
    quote: str
    verified: bool
    confidence: float

class GroundedSearchResponse(BaseModel):
    query: str
    category: SearchCategory
    answer: str
    citations: List[GroundedCitation]
    sources: List[SearchResultItem]

class BaseSearchProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def search(
        self,
        query: str,
        category: SearchCategory = SearchCategory.WEB,
        max_results: int = 5
    ) -> List[SearchResultItem]:
        pass
