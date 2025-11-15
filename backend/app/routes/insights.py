"""Insights and analytics endpoints."""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.models.base import get_db
from app.models.correlation import Correlation
from app.models.pattern import Pattern
from app.schemas.insights import CorrelationResponse, PatternResponse, DashboardSummary

router = APIRouter(prefix="/insights", tags=["insights"])

MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.get("/correlations", response_model=List[CorrelationResponse])
async def get_correlations(
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get discovered correlations."""
    query = (
        select(Correlation)
        .where(Correlation.user_id == MOCK_USER_ID)
        .order_by(Correlation.correlation_coefficient.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    correlations = result.scalars().all()
    return correlations


@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns(
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get discovered patterns."""
    query = (
        select(Pattern)
        .where(Pattern.user_id == MOCK_USER_ID)
        .order_by(Pattern.discovered_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    patterns = result.scalars().all()
    return patterns


@router.post("/trigger-analysis")
async def trigger_analysis(background_tasks: BackgroundTasks):
    """Manually trigger pattern discovery and correlation analysis."""
    # Import tasks here to avoid circular imports
    from app.tasks import run_full_analysis

    # Schedule background task
    task = run_full_analysis.delay(str(MOCK_USER_ID))

    return {
        "status": "analysis_started",
        "task_id": task.id,
        "message": "Pattern discovery and correlation analysis queued"
    }


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    period_days: int = 7
):
    """Get dashboard summary with key metrics."""
    # This is a simplified version - implement full aggregation logic
    from sqlalchemy import func
    from app.models.aggregate import DailyAggregate
    from datetime import datetime, timedelta

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
            DailyAggregate.user_id == MOCK_USER_ID,
            DailyAggregate.date >= start_date,
            DailyAggregate.date <= end_date
        )
    )

    result = await db.execute(agg_query)
    stats = result.one_or_none()

    # Get top correlations
    corr_query = (
        select(Correlation)
        .where(Correlation.user_id == MOCK_USER_ID)
        .order_by(Correlation.correlation_coefficient.desc())
        .limit(3)
    )
    corr_result = await db.execute(corr_query)
    correlations = corr_result.scalars().all()

    # Get recent patterns
    pattern_query = (
        select(Pattern)
        .where(Pattern.user_id == MOCK_USER_ID)
        .order_by(Pattern.discovered_at.desc())
        .limit(3)
    )
    pattern_result = await db.execute(pattern_query)
    patterns = pattern_result.scalars().all()

    return DashboardSummary(
        period_days=period_days,
        avg_glucose=float(stats.avg_glucose or 0),
        time_in_range_percent=float(stats.tir or 0),
        avg_sleep_hours=float(stats.avg_sleep or 0) / 60 if stats.avg_sleep else None,
        total_exercise_minutes=int(stats.total_exercise or 0),
        top_correlations=correlations,
        recent_patterns=patterns
    )
