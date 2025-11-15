"""GlucoLens Backend - FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.models.base import engine, Base
from app.routes import (
    glucose, sleep, activities, meals, insights, auth, advanced_insights,
    hba1c, medications, insulin, blood_pressure, body_metrics
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    print("🚀 GlucoLens Backend Starting...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1]}")
    print(f"🔴 Redis: {settings.REDIS_URL}")

    # Create tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        # Note: Uncomment this for initial development
        # await conn.run_sync(Base.metadata.create_all)
        pass

    yield

    # Shutdown
    print("🛑 GlucoLens Backend Shutting Down...")
    await engine.dispose()


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
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "glucolens-backend",
        "version": "2.0.0",
        "features": ["authentication", "advanced-ml", "real-time-alerts"]
    }


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
