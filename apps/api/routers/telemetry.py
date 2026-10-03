import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from apps.api.auth import get_optional_user
from services.observability.metrics import telemetry_collector, RequestTrace

logger = logging.getLogger("nova.api.telemetry")

router = APIRouter(tags=["Observability & Telemetry"])

@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Prometheus exposition metrics endpoint."""
    content = telemetry_collector.export_prometheus_text()
    return PlainTextResponse(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")

@router.get("/api/v1/telemetry/stats")
async def get_telemetry_stats(user: Optional[dict] = Depends(get_optional_user)):
    """Retrieves operational telemetry statistics and latency percentiles."""
    return telemetry_collector.get_dashboard_stats()

@router.get("/api/v1/telemetry/traces", response_model=List[RequestTrace])
async def get_recent_request_traces(limit: int = 50, user: Optional[dict] = Depends(get_optional_user)):
    """Retrieves recent traced HTTP requests."""
    return telemetry_collector.get_recent_traces(limit=limit)
