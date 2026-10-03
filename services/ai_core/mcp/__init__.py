"""
NOVA X Model Context Protocol (MCP) Subsystem
Connects external tools, data sources, and services via the standardized MCP JSON-RPC protocol.
"""

from .types import MCPServerConfig, MCPTool, MCPResource, MCPCallRequest, MCPCallResult
from .manager import MCPClientManager, mcp_manager

__all__ = [
    "MCPServerConfig",
    "MCPTool",
    "MCPResource",
    "MCPCallRequest",
    "MCPCallResult",
    "MCPClientManager",
    "mcp_manager",
]
