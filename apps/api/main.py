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
from apps.api.routers import health, auth, chat

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

# Request Tracing Middleware
@app.middleware("http")
async def trace_and_timing_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["x-request-id"] = request_id
    response.headers["x-process-time-ms"] = f"{process_time:.2f}"
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
