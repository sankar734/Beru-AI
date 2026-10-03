import uuid
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.config import settings
from apps.api.database import db_manager
from apps.api.redis_client import redis_manager
from apps.api.routers import health, auth, chat, models, search, files, research, projects, memory, media, code, artifacts, learning, experts, tools, agents, workflows, tasks, autopilot, desktop, desktop_files, screen, browser, developer, voice_control, mcp, security_audit, telemetry
from services.security import rate_limiter
from services.observability import telemetry_collector


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nova.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NOVA X Backend Services...")
    await db_manager.connect()
    await redis_manager.connect()
    yield
    logger.info("Shutting down NOVA X Backend Services...")

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Backend API Gateway and Orchestration Service for NOVA X Personal Intelligence Operating System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Tracing & Security Middleware
@app.middleware("http")
async def trace_and_timing_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    # Rate Limiting Check (per IP/host)
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, remaining, retry_after = rate_limiter.check_rate_limit(client_ip, limit=500, window_seconds=60)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Rate limit threshold exceeded."},
            headers={"Retry-After": str(retry_after)}
        )

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["x-request-id"] = request_id
    response.headers["x-process-time-ms"] = f"{process_time:.2f}"
    response.headers["x-ratelimit-remaining"] = str(remaining)

    # Telemetry Collection
    telemetry_collector.record_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=process_time,
        client_ip=client_ip
    )

    # Security Hardening Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response



# Root route
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "tagline": "Think. Search. Research. Create. Code. Learn. Act.",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# Register Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")
app.include_router(code.router, prefix="/api/v1")
app.include_router(artifacts.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(experts.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(autopilot.router, prefix="/api/v1")
app.include_router(desktop.router, prefix="/api/v1")
app.include_router(desktop_files.router, prefix="/api/v1")
app.include_router(screen.router, prefix="/api/v1")
app.include_router(browser.router, prefix="/api/v1")
app.include_router(developer.router, prefix="/api/v1")
app.include_router(voice_control.router, prefix="/api/v1")
app.include_router(mcp.router, prefix="/api/v1")
app.include_router(security_audit.router, prefix="/api/v1")
app.include_router(telemetry.router)

