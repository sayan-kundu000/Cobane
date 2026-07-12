from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.responses import StandardJSONResponse
from app.core.logging import app_logger

router = APIRouter(prefix="/health", tags=["health-diagnostics"])


@router.get("", response_class=StandardJSONResponse)
async def check_general_health():
    """General health check returning service operational indicator."""
    return {"status": "operational", "version": "1.0.0"}


@router.get("/liveness", response_class=StandardJSONResponse)
async def check_liveness():
    """Liveness check confirming app process execution."""
    return {"status": "alive"}


@router.get("/readiness", response_class=StandardJSONResponse)
async def check_readiness(db: AsyncSession = Depends(get_db)):
    """Readiness check validating connection states for database engines."""
    try:
        # Check database accessibility
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        app_logger.error("Readiness check failed database connection diagnostics: %s", str(e))
        return StandardJSONResponse(status_code=503, content={"status": "unready", "database": "disconnected"})
