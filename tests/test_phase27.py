import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from services.observability.metrics import telemetry_collector

client = TestClient(app)

def test_prometheus_metrics_endpoint():
    # Make a few sample requests
    client.get("/api/v1/health")
    client.get("/api/v1/mcp/servers")

    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    text = resp.text
    assert "# HELP nova_uptime_seconds" in text
    assert "# HELP nova_http_requests_total" in text
    assert "# HELP nova_http_request_duration_ms" in text
    assert "nova_http_requests_total{" in text

def test_telemetry_stats_and_percentiles():
    # Feed controlled latencies
    for lat in [10.0, 20.0, 30.0, 40.0, 50.0, 100.0, 200.0]:
        telemetry_collector.record_request(
            request_id="test_req",
            method="GET",
            path="/api/v1/health",
            status_code=200,
            duration_ms=lat
        )

    resp = client.get("/api/v1/telemetry/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_requests"] > 0
    assert "latencies_ms" in data
    latencies = data["latencies_ms"]
    assert "p50" in latencies
    assert "p95" in latencies
    assert "p99" in latencies
    assert latencies["p50"] > 0
    assert data["status"] in ["HEALTHY", "DEGRADED"]

def test_request_traces_recording():
    # Execute distinct traced request
    resp = client.get("/api/v1/health", headers={"x-request-id": "trace-test-uuid-999"})
    assert resp.status_code == 200

    traces_resp = client.get("/api/v1/telemetry/traces?limit=10")
    assert traces_resp.status_code == 200
    traces = traces_resp.json()
    assert len(traces) > 0
    match = next((t for t in traces if t["request_id"] == "trace-test-uuid-999"), None)
    assert match is not None
    assert match["method"] == "GET"
    assert match["path"] == "/api/v1/health"
    assert match["duration_ms"] >= 0

def test_ai_tokens_counter():
    telemetry_collector.record_tokens(prompt_tokens=150, completion_tokens=350)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    text = resp.text
    assert 'nova_ai_tokens_total{type="prompt"}' in text
    assert 'nova_ai_tokens_total{type="completion"}' in text
