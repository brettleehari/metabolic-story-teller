"""Insights and analytics endpoints."""
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, timedelta

from app.models.base import get_db
from app.models.user import User
from app.models.correlation import Correlation
from app.models.pattern import Pattern
from app.models.aggregate import DailyAggregate
from app.schemas.insights import CorrelationResponse, PatternResponse, DashboardSummary
from app.dependencies import get_current_user

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/correlations", response_model=List[CorrelationResponse])
async def get_correlations(
    limit: int = Query(10, le=100, description="Maximum number of correlations"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get discovered correlations (requires authentication)."""
    query = (
        select(Correlation)
        .where(Correlation.user_id == current_user.id)
        .order_by(Correlation.correlation_coefficient.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    correlations = result.scalars().all()
    return correlations


@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns(
    limit: int = Query(10, le=100, description="Maximum number of patterns"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get discovered patterns (requires authentication)."""
    query = (
        select(Pattern)
        .where(Pattern.user_id == current_user.id)
        .order_by(Pattern.discovered_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    patterns = result.scalars().all()
    return patterns


@router.post("/trigger-analysis")
async def trigger_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Manually trigger pattern discovery and correlation analysis (requires authentication)."""
    # Import tasks here to avoid circular imports
    from app.tasks import run_full_analysis

    # Schedule background task for current user
    task = run_full_analysis.delay(str(current_user.id))

    return {
        "status": "analysis_started",
        "task_id": task.id,
        "message": "Pattern discovery and correlation analysis queued"
    }


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    period_days: int = Query(7, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary with key metrics (requires authentication)."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=period_days)

    # Get aggregates
    agg_query = (
        select(
            func.avg(DailyAggregate.avg_glucose).label("avg_glucose"),
            func.avg(DailyAggregate.time_in_range_percent).label("tir"),
            func.avg(DailyAggregate.total_sleep_minutes).label("avg_sleep"),
            func.sum(DailyAggregate.total_exercise_minutes).label("total_exercise")
        )
        .where(
            DailyAggregate.user_id == current_user.id,
            DailyAggregate.date >= start_date,
            DailyAggregate.date <= end_date
        )
    )

    result = await db.execute(agg_query)
    stats = result.one_or_none()

    # Get top correlations
    corr_query = (
        select(Correlation)
        .where(Correlation.user_id == current_user.id)
        .order_by(Correlation.correlation_coefficient.desc())
        .limit(3)
    )
    corr_result = await db.execute(corr_query)
    correlations = corr_result.scalars().all()

    # Get recent patterns
    pattern_query = (
        select(Pattern)
        .where(Pattern.user_id == current_user.id)
        .order_by(Pattern.discovered_at.desc())
        .limit(3)
    )
    pattern_result = await db.execute(pattern_query)
    patterns = pattern_result.scalars().all()

    return DashboardSummary(
        period_days=period_days,
        avg_glucose=float(stats.avg_glucose or 0) if stats else 0.0,
        time_in_range_percent=float(stats.tir or 0) if stats else 0.0,
        avg_sleep_hours=float(stats.avg_sleep or 0) / 60 if (stats and stats.avg_sleep) else None,
        total_exercise_minutes=int(stats.total_exercise or 0) if stats else 0,
        top_correlations=correlations,
        recent_patterns=patterns
    )
