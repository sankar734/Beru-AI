"""NOVA X - Artifact Studio Models
Data structures for multi-format artifacts (Code, Web Apps, Documents, Diagrams, Reports, Presentations)
with version snapshot tracking.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class ArtifactVersion(BaseModel):
    version: int
    content: str
    summary: str = "Initial version"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ArtifactBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., description="DOCUMENT, REPORT, CODE, WEB_APP, DIAGRAM, PRESENTATION")
    description: Optional[str] = Field(default="")
    tags: List[str] = Field(default_factory=list)


class ArtifactCreate(ArtifactBase):
    initial_content: str = Field(..., description="Initial payload of the artifact")


class ArtifactUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    new_content: Optional[str] = None
    version_summary: Optional[str] = "Updated content"


class ArtifactResponse(ArtifactBase):
    id: str
    user_id: str
    current_version: int
    versions: List[ArtifactVersion]
    created_at: str
    updated_at: str


class ArtifactDiffResponse(BaseModel):
    artifact_id: str
    v1: int
    v2: int
    diff_lines: List[str]
    has_changes: bool
