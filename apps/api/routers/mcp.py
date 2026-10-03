import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from apps.api.auth import get_optional_user
from services.ai_core.mcp.types import MCPServerConfig, MCPTool, MCPResource, MCPCallRequest, MCPCallResult
from services.ai_core.mcp.manager import mcp_manager

logger = logging.getLogger("nova.api.mcp")

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])

@router.get("/servers", response_model=List[MCPServerConfig])
async def list_mcp_servers(user: Optional[dict] = Depends(get_optional_user)):
    """Lists registered Model Context Protocol servers and connectivity status."""
    return mcp_manager.list_servers()

@router.post("/servers", response_model=MCPServerConfig)
async def register_mcp_server(config: MCPServerConfig, user: Optional[dict] = Depends(get_optional_user)):
    """Registers a new external MCP server configuration."""
    return mcp_manager.register_server(config)

@router.get("/tools", response_model=List[MCPTool])
async def list_mcp_tools(server_id: Optional[str] = None, user: Optional[dict] = Depends(get_optional_user)):
    """Lists discovered tools across all or specific MCP servers."""
    return mcp_manager.list_tools(server_id=server_id)

@router.get("/resources", response_model=List[MCPResource])
async def list_mcp_resources(server_id: Optional[str] = None, user: Optional[dict] = Depends(get_optional_user)):
    """Lists discovered resources available via MCP protocol."""
    return mcp_manager.list_resources(server_id=server_id)

@router.post("/call", response_model=MCPCallResult)
async def call_mcp_tool(req: MCPCallRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Invokes an MCP tool with schema validation and Zero-Trust risk barriers."""
    result = await mcp_manager.call_tool(
        server_id=req.server_id,
        tool_name=req.tool_name,
        arguments=req.arguments,
        human_approved=req.human_approved
    )
    if result.status == "AWAITING_APPROVAL":
        raise HTTPException(
            status_code=403,
            detail=result.message or f"Tool '{req.tool_name}' requires human confirmation token."
        )
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message or "MCP Tool execution failed.")
    return result
