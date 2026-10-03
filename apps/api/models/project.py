from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = ""
    system_instructions: Optional[str] = ""
    custom_rules: Optional[List[str]] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_instructions: Optional[str] = None
    custom_rules: Optional[List[str]] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    system_instructions: str
    custom_rules: List[str]
    file_count: int = 0
    artifact_count: int = 0
    task_count: int = 0
    created_at: str
    updated_at: str
