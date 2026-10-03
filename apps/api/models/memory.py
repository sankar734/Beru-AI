from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class MemoryType(str, Enum):
    PREFERENCE = "PREFERENCE"
    PROJECT_CONTEXT = "PROJECT_CONTEXT"
    STABLE_FACT = "STABLE_FACT"
    RECURRING_WORKFLOW = "RECURRING_WORKFLOW"

class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: MemoryType = MemoryType.PREFERENCE
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None

class MemoryResponse(BaseModel):
    id: str
    user_id: str
    content: str
    memory_type: MemoryType
    project_id: Optional[str] = None
    is_active: bool = True
    tags: List[str]
    created_at: str
    updated_at: str

class KnowledgeEntity(BaseModel):
    id: str
    user_id: str
    entity_type: str  # Project, File, Concept, Technology, Task, Artifact
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeRelation(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation_type: str  # USES, DEPENDS_ON, REFERENCES, CONTAINS, RELATED_TO
