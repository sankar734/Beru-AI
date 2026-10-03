import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_mcp_servers_and_resources():
    # 1. List Servers
    resp = client.get("/api/v1/mcp/servers")
    assert resp.status_code == 200
    servers = resp.json()
    assert len(servers) >= 3
    server_ids = [s["server_id"] for s in servers]
    assert "github" in server_ids
    assert "postgres" in server_ids
    assert "filesystem" in server_ids

    # 2. List Resources
    res_resp = client.get("/api/v1/mcp/resources")
    assert res_resp.status_code == 200
    resources = res_resp.json()
    assert len(resources) >= 3
    uris = [r["uri"] for r in resources]
    assert any("github://" in u for u in uris)
    assert any("postgres://" in u for u in uris)

def test_mcp_tools_discovery_and_safe_call():
    # 1. List Tools
    tools_resp = client.get("/api/v1/mcp/tools")
    assert tools_resp.status_code == 200
    tools = tools_resp.json()
    assert len(tools) >= 5
    tool_names = [t["name"] for t in tools]
    assert "github_list_repos" in tool_names
    assert "postgres_inspect_schema" in tool_names
    assert "fs_read_file" in tool_names

    # 2. Safe execution (Level 1)
    call_resp = client.post("/api/v1/mcp/call", json={
        "server_id": "github",
        "tool_name": "github_list_repos",
        "arguments": {"org": "nova-intelligence"},
        "human_approved": False
    })
    assert call_resp.status_code == 200
    call_data = call_resp.json()
    assert call_data["success"] is True
    assert call_data["status"] == "SUCCESS"
    assert isinstance(call_data["result"], list)
    assert len(call_data["result"]) >= 2

def test_mcp_zero_trust_policy_barrier_for_level_3():
    # 1. Level 3 tool without approval must be blocked with 403
    blocked_resp = client.post("/api/v1/mcp/call", json={
        "server_id": "github",
        "tool_name": "github_create_issue",
        "arguments": {"repo": "core-engine", "title": "Critical Bug"},
        "human_approved": False
    })
    assert blocked_resp.status_code == 403
    assert "human authorization token" in blocked_resp.json()["detail"]


    # 2. Level 3 tool with human approval succeeds
    approved_resp = client.post("/api/v1/mcp/call", json={
        "server_id": "github",
        "tool_name": "github_create_issue",
        "arguments": {"repo": "core-engine", "title": "Critical Bug"},
        "human_approved": True
    })
    assert approved_resp.status_code == 200
    data = approved_resp.json()
    assert data["success"] is True
    assert data["result"]["issue_id"] == 104
    assert data["risk_level"] == 3

def test_dynamic_mcp_server_registration():
    new_server = {
        "server_id": "custom_slack",
        "name": "Slack Enterprise Workspace",
        "transport": "sse",
        "url": "https://slack.example.com/mcp",
        "status": "CONNECTED",
        "description": "Team messaging and automated incident response channel",
        "tools_count": 3,
        "resources_count": 1
    }
    reg_resp = client.post("/api/v1/mcp/servers", json=new_server)
    assert reg_resp.status_code == 200
    assert reg_resp.json()["server_id"] == "custom_slack"

    # Verify server is in list
    servers_resp = client.get("/api/v1/mcp/servers")
    assert any(s["server_id"] == "custom_slack" for s in servers_resp.json())
