"""NOVA X - Custom AI Experts Models
Data models for domain-specialized AI personas, system directives, and capability matrices.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class ExpertBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    avatar_icon: str = Field(default="Brain", description="Lucide icon name")
    color_theme: str = Field(default="purple", description="purple, cyan, emerald, amber, rose, blue")
    system_prompt: str = Field(..., min_length=10)
    capabilities: List[str] = Field(default_factory=list)
    temperature: float = Field(default=0.4, ge=0.0, le=1.0)


class ExpertCreate(ExpertBase):
    pass


class ExpertUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    avatar_icon: Optional[str] = None
    color_theme: Optional[str] = None
    system_prompt: Optional[str] = None
    capabilities: Optional[List[str]] = None
    temperature: Optional[float] = None


class ExpertResponse(ExpertBase):
    id: str
    user_id: str
    is_system_default: bool = False
    created_at: str
    updated_at: str


class ExpertConsultRequest(BaseModel):
    query: str
    context: Optional[str] = None


class ExpertConsultResponse(BaseModel):
    expert_id: str
    expert_name: str
    role: str
    consultation_response: str
    key_recommendations: List[str]
    suggested_followups: List[str]
