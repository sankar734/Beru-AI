from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CitationModel(BaseModel):
    id: str
    title: str
    snippet: str
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    page_number: Optional[int] = None
    confidence_score: float = 1.0

class AttachmentModel(BaseModel):
    id: str
    file_name: str
    file_size: int
    mime_type: str
    storage_path: str
    extracted_text_preview: Optional[str] = None

class ToolCallModel(BaseModel):
    id: str
    tool_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "completed"
    result: Optional[Any] = None

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    mode: Optional[str] = "AUTO"
    attachments: Optional[List[AttachmentModel]] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    mode: Optional[str] = "AUTO"
    citations: Optional[List[CitationModel]] = None
    attachments: Optional[List[AttachmentModel]] = None
    tool_calls: Optional[List[ToolCallModel]] = None
    thought_process: Optional[str] = None
    created_at: str

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    mode: Optional[str] = "AUTO"
    project_id: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    mode: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    mode: str
    project_id: Optional[str] = None
    pinned: bool = False
    archived: bool = False
    created_at: str
    updated_at: str
    message_count: Optional[int] = 0

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = Field(default_factory=list)
