"""GlucoLens Backend - FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DBAPIError
import logging

from app.config import settings
from app.models.base import engine, Base
from app.routes import (
    glucose, sleep, activities, meals, insights, auth, advanced_insights,
    hba1c, medications, insulin, blood_pressure, body_metrics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((OperationalError, DBAPIError, ConnectionRefusedError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
async def wait_for_database():
    """
    Wait for database to be ready with exponential backoff.

    Retries up to 5 times with exponential backoff:
    - Attempt 1: immediate
    - Attempt 2: wait 2s
    - Attempt 3: wait 4s
    - Attempt 4: wait 8s
    - Attempt 5: wait 16s

    Raises:
        OperationalError: If database is still not available after all retries
    """
    logger.info("Testing database connection...")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("✅ Database connection successful")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("🚀 GlucoLens Backend Starting...")
    logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[1]}")
    logger.info(f"🔴 Redis: {settings.REDIS_URL}")

    # Wait for database to be ready (with retry logic)
    try:
        await wait_for_database()
    except Exception as e:
        logger.error(f"❌ Failed to connect to database after retries: {e}")
        raise

    # Create tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        # Note: Uncomment this for initial development
        # await conn.run_sync(Base.metadata.create_all)
        pass

    logger.info("✅ GlucoLens Backend Ready")
    yield

    # Shutdown
    logger.info("🛑 GlucoLens Backend Shutting Down...")
    await engine.dispose()
    logger.info("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="GlucoLens API",
    description="Time-series glucose monitoring with ML-powered insights - MVP2",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connectivity test.

    Returns:
        200: Service is healthy and database is reachable
        503: Service is unhealthy (database unreachable)
    """
    from fastapi import status
    from fastapi.responses import JSONResponse

    health_status = {
        "service": "glucolens-backend",
        "version": "2.0.0",
        "features": ["authentication", "advanced-ml", "real-time-alerts"],
        "database": "unknown",
        "status": "unhealthy"
    }

    # Test database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        health_status["status"] = "healthy"
        return JSONResponse(content=health_status, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.warning(f"Health check failed - database unreachable: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"
        health_status["error"] = str(type(e).__name__)
        return JSONResponse(content=health_status, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


# Include routers
app.include_router(auth.router, prefix="/api/v1")  # Auth routes (no auth required)
app.include_router(glucose.router, prefix="/api/v1")
app.include_router(sleep.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")
app.include_router(meals.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(advanced_insights.router, prefix="/api/v1")  # PCMCI + STUMPY
app.include_router(hba1c.router, prefix="/api/v1")  # HbA1c tracking
app.include_router(medications.router, prefix="/api/v1")  # Medications management
app.include_router(insulin.router, prefix="/api/v1")  # Insulin doses
app.include_router(blood_pressure.router, prefix="/api/v1")  # Blood pressure
app.include_router(body_metrics.router, prefix="/api/v1")  # Body metrics


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GlucoLens API - MVP2",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "JWT Authentication",
            "PCMCI Causal Discovery",
            "STUMPY Pattern Detection",
            "Real-time Alerts (WebSocket)",
            "Apple HealthKit Integration"
        ]
    }
