import time
import logging
from collections import deque
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("nova.developer.supervisor")

class SupervisedService(BaseModel):
    id: str
    name: str
    command: str
    status: str = "ONLINE"  # ONLINE, STOPPED, RESTARTING, FAILED
    port: Optional[int] = None
    pid: Optional[int] = None
    started_at: float = Field(default_factory=time.time)
    restarts_count: int = 0
    health_endpoint: Optional[str] = None
    description: str = ""

class DevSupervisor:
    """Supervises and manages local development services and background processes."""

    def __init__(self):
        self._services: Dict[str, SupervisedService] = {
            "web-client": SupervisedService(
                id="web-client",
                name="Frontend Web Client",
                command="npm run dev --workspace=apps/web",
                status="ONLINE",
                port=5173,
                pid=10204,
                health_endpoint="http://localhost:5173",
                description="Vite React 19 Client with Tailwind and Zustand"
            ),
            "api-gateway": SupervisedService(
                id="api-gateway",
                name="FastAPI Gateway",
                command="uvicorn apps.api.main:app --port 8000 --reload",
                status="ONLINE",
                port=8000,
                pid=14880,
                health_endpoint="http://127.0.0.1:8000/api/v1/health",
                description="NOVA X Core Gateway & Orchestration API"
            ),
            "background-worker": SupervisedService(
                id="background-worker",
                name="Agent Task Worker",
                command="python -m services.agent_worker",
                status="ONLINE",
                pid=19280,
                description="Autonomous Agent Goal Executor & Background Telemetry"
            )
        }
        self._log_buffers: Dict[str, deque] = {
            s_id: deque(maxlen=200) for s_id in self._services
        }
        self._seed_initial_logs()

    def _seed_initial_logs(self):
        now = time.strftime("%H:%M:%S")
        self._log_buffers["web-client"].append(f"[{now}] [vite] ready in 340ms at http://localhost:5173/")
        self._log_buffers["api-gateway"].append(f"[{now}] INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)")
        self._log_buffers["api-gateway"].append(f"[{now}] INFO: Initializing NOVA X Backend Services...")
        self._log_buffers["background-worker"].append(f"[{now}] [worker] Agent task engine initialized and awaiting goals")

    def list_services(self) -> List[SupervisedService]:
        return list(self._services.values())

    def get_service(self, service_id: str) -> Optional[SupervisedService]:
        return self._services.get(service_id)

    def restart_service(self, service_id: str) -> SupervisedService:
        if service_id not in self._services:
            raise KeyError(f"Unknown service: {service_id}")
        
        service = self._services[service_id]
        service.status = "RESTARTING"
        service.restarts_count += 1
        now = time.strftime("%H:%M:%S")
        self._log_buffers[service_id].append(f"[{now}] [supervisor] Received restart signal for {service.name}")
        
        # Emulate rapid supervisor cycle back to ONLINE
        service.started_at = time.time()
        service.status = "ONLINE"
        self._log_buffers[service_id].append(f"[{now}] [supervisor] {service.name} successfully re-spawned (PID: {service.pid})")
        return service

    def stop_service(self, service_id: str) -> SupervisedService:
        if service_id not in self._services:
            raise KeyError(f"Unknown service: {service_id}")
        service = self._services[service_id]
        service.status = "STOPPED"
        now = time.strftime("%H:%M:%S")
        self._log_buffers[service_id].append(f"[{now}] [supervisor] {service.name} stopped gracefully")
        return service

    def append_log(self, service_id: str, line: str):
        if service_id in self._log_buffers:
            now = time.strftime("%H:%M:%S")
            self._log_buffers[service_id].append(f"[{now}] {line}")

    def get_logs(self, service_id: str, limit: int = 50) -> List[str]:
        if service_id not in self._log_buffers:
            return []
        buf = list(self._log_buffers[service_id])
        return buf[-limit:]

dev_supervisor = DevSupervisor()
