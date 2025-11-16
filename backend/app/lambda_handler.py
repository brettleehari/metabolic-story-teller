"""
AWS Lambda handler for GlucoLens Demo (Read-Only).

This module provides a simplified FastAPI application optimized for
AWS Lambda deployment with read-only endpoints for demo purposes.

Features:
- No authentication required (demo mode)
- GET endpoints only
- Optimized for cold starts
- Mangum integration for Lambda compatibility
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from app.config import async_session_maker
from app.models.user import User
from app.models.glucose import GlucoseReading
from app.models.correlation import Correlation
from app.models.pattern import Pattern
from app.models.aggregate import DailyAggregate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GlucoLens Demo API",
    description="Read-only demo API for GlucoLens",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GlucoLens Demo API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "users": "/users",
            "insights": "/insights/{user_id}",
            "correlations": "/correlations/{user_id}",
            "patterns": "/patterns/{user_id}",
            "dashboard": "/dashboard/{user_id}",
            "glucose": "/glucose/readings/{user_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/users")
async def get_demo_users():
    """
    Get list of demo user profiles.

    Returns:
        List of demo users with id, name, age, and diabetes type
    """
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            return {
                "count": len(users),
                "users": [
                    {
                        "id": str(user.id),
                        "full_name": user.full_name,
                        "age": user.age,
                        "gender": user.gender,
                        "diabetes_type": user.diabetes_type,
                        "target_range_min": user.target_range_min,
                        "target_range_max": user.target_range_max,
                    }
                    for user in users
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insights/{user_id}")
async def get_insights(user_id: str):
    """
    Get insights summary for a demo user.

    Args:
        user_id: UUID of the demo user

    Returns:
        Combined insights with correlations and patterns
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    try:
        async with async_session_maker() as session:
            # Verify user exists
            user_result = await session.execute(
                select(User).where(User.id == user_uuid)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get top correlations
            corr_query = select(Correlation).where(
                Correlation.user_id == user_uuid
            ).order_by(Correlation.abs_correlation.desc()).limit(10)
            corr_result = await session.execute(corr_query)
            correlations = corr_result.scalars().all()

            # Get patterns
            pattern_query = select(Pattern).where(
                Pattern.user_id == user_uuid
            ).order_by(Pattern.confidence.desc()).limit(10)
            pattern_result = await session.execute(pattern_query)
            patterns = pattern_result.scalars().all()

            return {
                "user_id": user_id,
                "user_name": user.full_name,
                "correlations": [
                    {
                        "id": c.id,
                        "factor_x": c.factor_x,
                        "factor_y": c.factor_y,
                        "correlation": round(c.correlation, 3),
                        "p_value": round(c.p_value, 4) if c.p_value else None,
                        "time_lag_days": c.time_lag_days,
                        "interpretation": _interpret_correlation(c.correlation)
                    }
                    for c in correlations
                ],
                "patterns": [
                    {
                        "id": p.id,
                        "type": p.pattern_type,
                        "description": p.description,
                        "confidence": round(p.confidence, 2),
                        "support": round(p.support, 3) if p.support else None,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in patterns
                ],
                "summary": {
                    "total_correlations": len(correlations),
                    "total_patterns": len(patterns),
                    "strongest_correlation": max([c.abs_correlation for c in correlations]) if correlations else 0
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/correlations/{user_id}")
async def get_correlations(user_id: str, limit: int = 20):
    """
    Get correlations for a user.

    Args:
        user_id: UUID of the user
        limit: Maximum number of correlations to return (default: 20)

    Returns:
        List of correlations ordered by strength
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    try:
        async with async_session_maker() as session:
            query = select(Correlation).where(
                Correlation.user_id == user_uuid
            ).order_by(Correlation.abs_correlation.desc()).limit(limit)

            result = await session.execute(query)
            correlations = result.scalars().all()

            return {
                "user_id": user_id,
                "count": len(correlations),
                "correlations": [
                    {
                        "factor_x": c.factor_x,
                        "factor_y": c.factor_y,
                        "correlation": round(c.correlation, 3),
                        "p_value": round(c.p_value, 4) if c.p_value else None,
                        "time_lag_days": c.time_lag_days,
                        "interpretation": _interpret_correlation(c.correlation)
                    }
                    for c in correlations
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patterns/{user_id}")
async def get_patterns(user_id: str, limit: int = 20):
    """
    Get discovered patterns for a user.

    Args:
        user_id: UUID of the user
        limit: Maximum number of patterns to return (default: 20)

    Returns:
        List of discovered patterns
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    try:
        async with async_session_maker() as session:
            query = select(Pattern).where(
                Pattern.user_id == user_uuid
            ).order_by(Pattern.confidence.desc()).limit(limit)

            result = await session.execute(query)
            patterns = result.scalars().all()

            return {
                "user_id": user_id,
                "count": len(patterns),
                "patterns": [
                    {
                        "type": p.pattern_type,
                        "description": p.description,
                        "confidence": round(p.confidence, 2),
                        "support": round(p.support, 3) if p.support else None,
                        "metadata": p.metadata,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in patterns
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{user_id}")
async def get_dashboard(
    user_id: str,
    period_days: int = 7
):
    """
    Get dashboard summary for a user.

    Args:
        user_id: UUID of the user
        period_days: Number of days to include (default: 7)

    Returns:
        Dashboard summary with aggregated metrics
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if period_days not in [7, 30, 90]:
        raise HTTPException(
            status_code=400,
            detail="period_days must be 7, 30, or 90"
        )

    try:
        async with async_session_maker() as session:
            # Get user
            user_result = await session.execute(
                select(User).where(User.id == user_uuid)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get recent aggregates
            start_date = datetime.now().date() - timedelta(days=period_days)

            agg_query = select(DailyAggregate).where(
                DailyAggregate.user_id == user_uuid,
                DailyAggregate.date >= start_date
            ).order_by(DailyAggregate.date.desc())

            agg_result = await session.execute(agg_query)
            aggregates = agg_result.scalars().all()

            if not aggregates:
                return {
                    "user_id": user_id,
                    "period_days": period_days,
                    "message": "No data available for this period"
                }

            # Calculate summary statistics
            avg_glucose = sum(a.avg_glucose for a in aggregates if a.avg_glucose) / len(aggregates)
            avg_tir = sum(a.time_in_range_pct for a in aggregates if a.time_in_range_pct) / len(aggregates)

            sleep_data = [a.total_sleep_minutes for a in aggregates if a.total_sleep_minutes]
            avg_sleep_hours = (sum(sleep_data) / len(sleep_data) / 60) if sleep_data else 0

            return {
                "user_id": user_id,
                "user_name": user.full_name,
                "period_days": period_days,
                "summary": {
                    "avg_glucose": round(avg_glucose, 1),
                    "time_in_range_pct": round(avg_tir, 1),
                    "avg_sleep_hours": round(avg_sleep_hours, 1),
                    "target_range": {
                        "min": user.target_range_min,
                        "max": user.target_range_max
                    }
                },
                "daily_data": [
                    {
                        "date": str(a.date),
                        "avg_glucose": round(a.avg_glucose, 1) if a.avg_glucose else None,
                        "min_glucose": round(a.min_glucose, 1) if a.min_glucose else None,
                        "max_glucose": round(a.max_glucose, 1) if a.max_glucose else None,
                        "time_in_range_pct": round(a.time_in_range_pct, 1) if a.time_in_range_pct else None,
                        "total_sleep_minutes": a.total_sleep_minutes,
                        "total_exercise_minutes": a.total_exercise_minutes,
                        "total_carbs_grams": round(a.total_carbs_grams, 1) if a.total_carbs_grams else None
                    }
                    for a in aggregates
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/glucose/readings/{user_id}")
async def get_glucose_readings(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 288  # 24 hours at 5-min intervals
):
    """
    Get glucose readings for a user.

    Args:
        user_id: UUID of the user
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        limit: Maximum number of readings (default: 288 = 24 hours)

    Returns:
        List of glucose readings
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    try:
        async with async_session_maker() as session:
            query = select(GlucoseReading).where(
                GlucoseReading.user_id == user_uuid
            )

            # Apply date filters if provided
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date)
                    query = query.where(GlucoseReading.timestamp >= start_dt)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid start_date format")

            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date)
                    query = query.where(GlucoseReading.timestamp <= end_dt)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid end_date format")

            query = query.order_by(GlucoseReading.timestamp.desc()).limit(limit)

            result = await session.execute(query)
            readings = result.scalars().all()

            return {
                "user_id": user_id,
                "count": len(readings),
                "limit": limit,
                "readings": [
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "value": r.value,
                        "source": r.source
                    }
                    for r in reversed(readings)  # Return in chronological order
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching glucose readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _interpret_correlation(correlation: float) -> str:
    """Interpret correlation strength."""
    abs_corr = abs(correlation)
    direction = "positive" if correlation > 0 else "negative"

    if abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.4:
        strength = "moderate"
    elif abs_corr >= 0.2:
        strength = "weak"
    else:
        strength = "very weak"

    return f"{strength} {direction}"


# Exception handler for all errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")
