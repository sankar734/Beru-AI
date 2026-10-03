import time
import logging
from typing import Dict, List, Optional, Any

from .types import MCPServerConfig, MCPTool, MCPResource, MCPCallResult

logger = logging.getLogger("nova.ai_core.mcp")

class MCPClientManager:
    """Manages connections to Model Context Protocol (MCP) servers, tool discovery, and guarded invocation."""

    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._tools: Dict[str, List[MCPTool]] = {}
        self._resources: Dict[str, List[MCPResource]] = {}
        self._init_builtin_servers()

    def _init_builtin_servers(self):
        # 1. GitHub MCP Server
        self._servers["github"] = MCPServerConfig(
            server_id="github",
            name="GitHub Integrations",
            transport="builtin",
            status="CONNECTED",
            description="Manage repositories, pull requests, and code search via GitHub API",
            tools_count=2,
            resources_count=1
        )
        self._tools["github"] = [
            MCPTool(
                name="github_list_repos",
                description="List public or authorized repositories for an organization or user",
                inputSchema={"type": "object", "properties": {"org": {"type": "string"}}},
                risk_level=1,
                server_id="github"
            ),
            MCPTool(
                name="github_create_issue",
                description="Create a new bug report or issue on a repository",
                inputSchema={"type": "object", "required": ["repo", "title"], "properties": {"repo": {"type": "string"}, "title": {"type": "string"}}},
                risk_level=3,  # Level 3: writes externally, requires human approval
                server_id="github"
            )
        ]
        self._resources["github"] = [
            MCPResource(
                uri="github://org/nova-x/config",
                name="Repository Config",
                description="Global organization repository settings",
                mimeType="application/json",
                server_id="github"
            )
        ]

        # 2. Postgres MCP Server
        self._servers["postgres"] = MCPServerConfig(
            server_id="postgres",
            name="PostgreSQL Database Inspector",
            transport="builtin",
            status="CONNECTED",
            description="Query database schemas and execute read-only SQL queries",
            tools_count=2,
            resources_count=1
        )
        self._tools["postgres"] = [
            MCPTool(
                name="postgres_inspect_schema",
                description="Inspect table schemas, column types, and foreign key relations",
                inputSchema={"type": "object", "properties": {"schema": {"type": "string", "default": "public"}}},
                risk_level=1,
                server_id="postgres"
            ),
            MCPTool(
                name="postgres_read_query",
                description="Execute a read-only SELECT query against authorized tables",
                inputSchema={"type": "object", "required": ["sql"], "properties": {"sql": {"type": "string"}}},
                risk_level=2,
                server_id="postgres"
            )
        ]
        self._resources["postgres"] = [
            MCPResource(
                uri="postgres://schema/public/ddl",
                name="Public Schema DDL",
                description="Exported schema definitions",
                mimeType="application/sql",
                server_id="postgres"
            )
        ]

        # 3. Filesystem Sandboxed MCP Server
        self._servers["filesystem"] = MCPServerConfig(
            server_id="filesystem",
            name="Sandboxed Filesystem MCP",
            transport="builtin",
            status="CONNECTED",
            description="Scoped file access within approved project directories",
            tools_count=2,
            resources_count=1
        )
        self._tools["filesystem"] = [
            MCPTool(
                name="fs_list_directory",
                description="List contents of an approved workspace directory",
                inputSchema={"type": "object", "properties": {"path": {"type": "string"}}},
                risk_level=1,
                server_id="filesystem"
            ),
            MCPTool(
                name="fs_read_file",
                description="Read contents of an approved workspace file",
                inputSchema={"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
                risk_level=1,
                server_id="filesystem"
            )
        ]
        self._resources["filesystem"] = [
            MCPResource(
                uri="file://workspace/README.md",
                name="Project Documentation",
                description="Root workspace README",
                mimeType="text/markdown",
                server_id="filesystem"
            )
        ]

    def list_servers(self) -> List[MCPServerConfig]:
        """Lists all registered MCP server adapters."""
        return list(self._servers.values())

    def register_server(self, config: MCPServerConfig) -> MCPServerConfig:
        """Dynamically registers or updates an MCP server adapter."""
        self._servers[config.server_id] = config
        if config.server_id not in self._tools:
            self._tools[config.server_id] = []
        if config.server_id not in self._resources:
            self._resources[config.server_id] = []
        return config

    def list_tools(self, server_id: Optional[str] = None) -> List[MCPTool]:
        """Lists all available tools across connected servers or for a specific server."""
        if server_id:
            return self._tools.get(server_id, [])
        all_tools = []
        for tools_list in self._tools.values():
            all_tools.extend(tools_list)
        return all_tools

    def list_resources(self, server_id: Optional[str] = None) -> List[MCPResource]:
        """Lists all available resources."""
        if server_id:
            return self._resources.get(server_id, [])
        all_res = []
        for res_list in self._resources.values():
            all_res.extend(res_list)
        return all_res

    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        human_approved: bool = False
    ) -> MCPCallResult:
        """Invokes an MCP tool, enforcing Zero-Trust risk barriers for Level 3/4."""
        t0 = time.time()

        if server_id not in self._servers:
            return MCPCallResult(
                success=False,
                status="FAILED",
                is_error=True,
                server_id=server_id,
                tool_name=tool_name,
                message=f"MCP Server '{server_id}' not found."
            )

        server_tools = self._tools.get(server_id, [])
        target_tool = next((t for t in server_tools if t.name == tool_name), None)

        if not target_tool:
            return MCPCallResult(
                success=False,
                status="FAILED",
                is_error=True,
                server_id=server_id,
                tool_name=tool_name,
                message=f"Tool '{tool_name}' not found on MCP Server '{server_id}'."
            )

        # Policy Gate: Level 3 or 4 requires human approval
        if target_tool.risk_level >= 3 and not human_approved:
            return MCPCallResult(
                success=False,
                status="AWAITING_APPROVAL",
                risk_level=target_tool.risk_level,
                server_id=server_id,
                tool_name=tool_name,
                message=f"Action '{tool_name}' is Risk Level {target_tool.risk_level} and requires explicit human authorization token."
            )

        # Execute Tool Logic
        result_payload = await self._dispatch_tool_execution(server_id, tool_name, arguments)
        elapsed_ms = round((time.time() - t0) * 1000, 2)

        return MCPCallResult(
            success=True,
            status="SUCCESS",
            result=result_payload,
            is_error=False,
            risk_level=target_tool.risk_level,
            server_id=server_id,
            tool_name=tool_name,
            execution_time_ms=elapsed_ms,
            message="Tool executed successfully."
        )

    async def _dispatch_tool_execution(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Internal execution handler for built-in MCP tools."""
        if server_id == "github":
            if tool_name == "github_list_repos":
                org = arguments.get("org", "nova-intelligence")
                return [
                    {"name": f"{org}/core-engine", "stars": 1420, "language": "Python"},
                    {"name": f"{org}/web-client", "stars": 880, "language": "TypeScript"}
                ]
            elif tool_name == "github_create_issue":
                return {
                    "issue_id": 104,
                    "repo": arguments.get("repo", "nova-x"),
                    "title": arguments.get("title", "New issue"),
                    "status": "OPEN",
                    "url": f"https://github.com/nova-x/{arguments.get('repo', 'core')}/issues/104"
                }

        elif server_id == "postgres":
            if tool_name == "postgres_inspect_schema":
                return {
                    "schema": arguments.get("schema", "public"),
                    "tables": ["users", "chat_sessions", "messages", "artifacts", "tools_log"]
                }
            elif tool_name == "postgres_read_query":
                return {
                    "sql": arguments.get("sql"),
                    "rows_returned": 2,
                    "rows": [{"id": 1, "status": "active"}, {"id": 2, "status": "pending"}]
                }

        elif server_id == "filesystem":
            if tool_name == "fs_list_directory":
                return ["apps", "services", "tests", "docs", "package.json", "pyproject.toml"]
            elif tool_name == "fs_read_file":
                return f"# Content for {arguments.get('path', 'file.txt')}\nNOVA X Master Build"

        return {"output": f"Executed {tool_name} with params {arguments}"}

mcp_manager = MCPClientManager()
