from fastapi import APIRouter, Depends
import psutil
import time
from apps.api.database import get_db, DatabaseManager
from apps.api.redis_client import redis_manager
from apps.api.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

START_TIME = time.time()

@router.get("")
async def health_check(db: DatabaseManager = Depends(get_db)):
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_info = psutil.virtual_memory()

    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "database": {
            "type": "mongodb" if not db.is_in_memory else "in-memory-fallback",
            "connected": True
        },
        "redis": {
            "type": "redis" if not redis_manager.is_in_memory else "in-memory-fallback",
            "connected": True
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_used_mb": round(memory_info.used / (1024 * 1024), 2),
            "memory_total_mb": round(memory_info.total / (1024 * 1024), 2)
        }
    }
