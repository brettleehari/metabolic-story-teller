"""Body metrics endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.body_metrics import BodyMetrics
from app.schemas.body_metrics import BodyMetricsCreate, BodyMetricsResponse, BodyMetricsBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/body-metrics", tags=["body-metrics"])


@router.post("/", response_model=BodyMetricsResponse, status_code=201)
async def create_body_metrics(
    metrics: BodyMetricsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record body metrics (weight, body composition, etc.)."""
    # Auto-calculate BMI if weight provided and user has height
    bmi = metrics.bmi
    if metrics.weight_kg and current_user.height_cm and not bmi:
        height_m = float(current_user.height_cm) / 100
        bmi = float(metrics.weight_kg) / (height_m ** 2)

    db_metrics = BodyMetrics(
        user_id=current_user.id,
        **metrics.model_dump(exclude={'bmi'}),
        bmi=bmi
    )
    db.add(db_metrics)
    await db.flush()
    await db.refresh(db_metrics)
    return db_metrics


@router.post("/bulk", status_code=201)
async def bulk_upload_body_metrics(
    data: BodyMetricsBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload body metrics."""
    height_m = float(current_user.height_cm) / 100 if current_user.height_cm else None

    db_metrics_list = []
    for metric in data.metrics:
        bmi = metric.bmi
        if metric.weight_kg and height_m and not bmi:
            bmi = float(metric.weight_kg) / (height_m ** 2)

        db_metric = BodyMetrics(
            user_id=current_user.id,
            **metric.model_dump(exclude={'bmi'}),
            bmi=bmi
        )
        db_metrics_list.append(db_metric)

    db.add_all(db_metrics_list)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_metrics_list),
        "start_time": db_metrics_list[0].timestamp if db_metrics_list else None,
        "end_time": db_metrics_list[-1].timestamp if db_metrics_list else None,
    }


@router.get("/", response_model=List[BodyMetricsResponse])
async def get_body_metrics(
    start_time: Optional[datetime] = Query(None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter until this timestamp"),
    lookback_days: int = Query(90, le=730, description="Days to look back (default 90)"),
    limit: int = Query(1000, le=10000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get body metrics for the authenticated user."""
    query = select(BodyMetrics).where(BodyMetrics.user_id == current_user.id)

    # Default to lookback_days if no start_time provided
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=lookback_days)

    query = query.where(BodyMetrics.timestamp >= start_time)

    if end_time:
        query = query.where(BodyMetrics.timestamp <= end_time)

    query = query.order_by(BodyMetrics.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    metrics = result.scalars().all()
    return metrics


@router.get("/latest", response_model=BodyMetricsResponse)
async def get_latest_body_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most recent body metrics."""
    query = select(BodyMetrics).where(
        BodyMetrics.user_id == current_user.id
    ).order_by(BodyMetrics.timestamp.desc()).limit(1)

    result = await db.execute(query)
    metrics = result.scalar_one_or_none()

    if not metrics:
        raise HTTPException(status_code=404, detail="No body metrics found")

    return metrics


@router.get("/stats")
async def get_body_metrics_statistics(
    lookback_days: int = Query(90, le=730, description="Days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get body metrics statistics and trends."""
    start_time = datetime.utcnow() - timedelta(days=lookback_days)

    query = select(BodyMetrics).where(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.timestamp >= start_time
    ).order_by(BodyMetrics.timestamp)

    result = await db.execute(query)
    metrics = result.scalars().all()

    if not metrics:
        return {"message": "No body metrics found in this period"}

    weight_values = [float(m.weight_kg) for m in metrics if m.weight_kg]
    bmi_values = [float(m.bmi) for m in metrics if m.bmi]
    body_fat_values = [float(m.body_fat_percent) for m in metrics if m.body_fat_percent]

    # Calculate weight change (first vs last)
    weight_change = None
    if len(weight_values) >= 2:
        weight_change = round(weight_values[-1] - weight_values[0], 2)

    return {
        "period_days": lookback_days,
        "total_readings": len(metrics),
        "weight_kg": {
            "current": weight_values[-1] if weight_values else None,
            "avg": round(sum(weight_values) / len(weight_values), 2) if weight_values else None,
            "min": round(min(weight_values), 2) if weight_values else None,
            "max": round(max(weight_values), 2) if weight_values else None,
            "change": weight_change
        } if weight_values else None,
        "bmi": {
            "current": round(bmi_values[-1], 1) if bmi_values else None,
            "avg": round(sum(bmi_values) / len(bmi_values), 1) if bmi_values else None,
        } if bmi_values else None,
        "body_fat_percent": {
            "current": round(body_fat_values[-1], 1) if body_fat_values else None,
            "avg": round(sum(body_fat_values) / len(body_fat_values), 1) if body_fat_values else None,
        } if body_fat_values else None
    }


@router.delete("/{metrics_id}", status_code=204)
async def delete_body_metrics(
    metrics_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a body metrics record."""
    query = select(BodyMetrics).where(
        BodyMetrics.id == metrics_id,
        BodyMetrics.user_id == current_user.id
    )

    result = await db.execute(query)
    metrics = result.scalar_one_or_none()

    if not metrics:
        raise HTTPException(status_code=404, detail="Body metrics not found")

    await db.delete(metrics)
    await db.flush()
    return None
