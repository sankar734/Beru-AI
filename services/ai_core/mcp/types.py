from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any] = Field(default_factory=dict)
    risk_level: int = 1
    server_id: str

class MCPResource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = "text/plain"
    server_id: str

class MCPServerConfig(BaseModel):
    server_id: str
    name: str
    transport: str = "builtin"  # "builtin", "stdio", "sse"
    command: Optional[str] = None
    url: Optional[str] = None
    status: str = "CONNECTED"  # "CONNECTED", "DISCONNECTED", "ERROR"
    description: str = ""
    tools_count: int = 0
    resources_count: int = 0

class MCPCallRequest(BaseModel):
    server_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    human_approved: bool = False

class MCPCallResult(BaseModel):
    success: bool
    status: str = "SUCCESS"  # SUCCESS, AWAITING_APPROVAL, FAILED
    result: Optional[Any] = None
    is_error: bool = False
    risk_level: int = 1
    server_id: str
    tool_name: str
    execution_time_ms: float = 0.0
    message: Optional[str] = None
