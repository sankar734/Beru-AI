import time
import math
import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("nova.observability")

class RequestTrace(BaseModel):
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    timestamp: float = Field(default_factory=time.time)
    client_ip: str = "127.0.0.1"

class TelemetryCollector:
    """Centralized metrics collection, latency percentile computation, and Prometheus exporter."""

    def __init__(self):
        self._start_time = time.time()
        self._requests_counter: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self._latencies_ms: deque = deque(maxlen=2000)
        self._traces: deque = deque(maxlen=200)
        self._tokens_counter = {"prompt": 0, "completion": 0, "total": 0}
        self._tool_invocations = defaultdict(int)
        self._active_connections = 0

    def record_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str = "127.0.0.1"
    ):
        """Records an HTTP request outcome and latency."""
        # Sanitize path to avoid cardinality explosion for IDs
        clean_path = path.split("?")[0]
        self._requests_counter[(method, clean_path, status_code)] += 1
        self._latencies_ms.append(duration_ms)
        self._traces.append(RequestTrace(
            request_id=request_id,
            method=method,
            path=clean_path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            timestamp=time.time(),
            client_ip=client_ip
        ))

    def record_tokens(self, prompt_tokens: int, completion_tokens: int):
        """Increments AI token consumption counters."""
        self._tokens_counter["prompt"] += prompt_tokens
        self._tokens_counter["completion"] += completion_tokens
        self._tokens_counter["total"] += (prompt_tokens + completion_tokens)

    def record_tool_call(self, tool_name: str, success: bool = True):
        status = "success" if success else "failure"
        self._tool_invocations[(tool_name, status)] += 1

    def calculate_percentiles(self) -> Dict[str, float]:
        """Calculates p50, p90, p95, and p99 response times in milliseconds."""
        if not self._latencies_ms:
            return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}

        sorted_latencies = sorted(list(self._latencies_ms))
        n = len(sorted_latencies)

        def pct(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_latencies[int(k)]
            d0 = sorted_latencies[int(f)] * (c - k)
            d1 = sorted_latencies[int(c)] * (k - f)
            return round(d0 + d1, 2)

        avg_lat = round(sum(sorted_latencies) / n, 2)
        return {
            "p50": pct(0.50),
            "p90": pct(0.90),
            "p95": pct(0.95),
            "p99": pct(0.99),
            "avg": avg_lat
        }

    def export_prometheus_text(self) -> str:
        """Formats collected telemetry as standard Prometheus exposition text."""
        lines = []
        lines.append("# HELP nova_uptime_seconds Total uptime in seconds")
        lines.append("# TYPE nova_uptime_seconds gauge")
        lines.append(f"nova_uptime_seconds {time.time() - self._start_time:.2f}")

        lines.append("# HELP nova_http_requests_total Total HTTP requests")
        lines.append("# TYPE nova_http_requests_total counter")
        for (m, p, s), count in self._requests_counter.items():
            lines.append(f'nova_http_requests_total{{method="{m}",path="{p}",status="{s}"}} {count}')

        percentiles = self.calculate_percentiles()
        lines.append("# HELP nova_http_request_duration_ms Request latency percentiles")
        lines.append("# TYPE nova_http_request_duration_ms summary")
        lines.append(f'nova_http_request_duration_ms{{quantile="0.5"}} {percentiles["p50"]}')
        lines.append(f'nova_http_request_duration_ms{{quantile="0.9"}} {percentiles["p90"]}')
        lines.append(f'nova_http_request_duration_ms{{quantile="0.95"}} {percentiles["p95"]}')
        lines.append(f'nova_http_request_duration_ms{{quantile="0.99"}} {percentiles["p99"]}')

        lines.append("# HELP nova_ai_tokens_total Total tokens processed")
        lines.append("# TYPE nova_ai_tokens_total counter")
        lines.append(f'nova_ai_tokens_total{{type="prompt"}} {self._tokens_counter["prompt"]}')
        lines.append(f'nova_ai_tokens_total{{type="completion"}} {self._tokens_counter["completion"]}')
        lines.append(f'nova_ai_tokens_total{{type="total"}} {self._tokens_counter["total"]}')

        return "\n".join(lines) + "\n"

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Provides structured health and performance summary for UI dashboards."""
        total_reqs = sum(self._requests_counter.values())
        error_reqs = sum(count for (_, _, s), count in self._requests_counter.items() if s >= 400)
        error_rate = round((error_reqs / total_reqs * 100), 2) if total_reqs > 0 else 0.0

        percentiles = self.calculate_percentiles()

        return {
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "total_requests": total_reqs,
            "error_requests": error_reqs,
            "error_rate_pct": error_rate,
            "latencies_ms": percentiles,
            "tokens_consumed": self._tokens_counter,
            "active_connections": self._active_connections,
            "status": "HEALTHY" if error_rate < 5.0 else "DEGRADED"
        }

    def get_recent_traces(self, limit: int = 50) -> List[RequestTrace]:
        return list(reversed(list(self._traces)[-limit:]))

telemetry_collector = TelemetryCollector()
