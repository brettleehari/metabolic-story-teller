"""Blood pressure endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.blood_pressure import BloodPressure
from app.schemas.blood_pressure import BloodPressureCreate, BloodPressureResponse, BloodPressureBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/blood-pressure", tags=["blood-pressure"])


@router.post("/readings", response_model=BloodPressureResponse, status_code=201)
async def create_blood_pressure_reading(
    reading: BloodPressureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a blood pressure reading."""
    db_reading = BloodPressure(
        user_id=current_user.id,
        **reading.model_dump()
    )
    db.add(db_reading)
    await db.flush()
    await db.refresh(db_reading)
    return db_reading


@router.post("/bulk", status_code=201)
async def bulk_upload_blood_pressure(
    data: BloodPressureBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload blood pressure readings."""
    db_readings = [
        BloodPressure(user_id=current_user.id, **reading.model_dump())
        for reading in data.readings
    ]
    db.add_all(db_readings)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_readings),
        "start_time": db_readings[0].timestamp if db_readings else None,
        "end_time": db_readings[-1].timestamp if db_readings else None,
    }


@router.get("/readings", response_model=List[BloodPressureResponse])
async def get_blood_pressure_readings(
    start_time: Optional[datetime] = Query(None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter until this timestamp"),
    lookback_days: int = Query(30, le=365, description="Days to look back (default 30)"),
    limit: int = Query(1000, le=10000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get blood pressure readings for the authenticated user."""
    query = select(BloodPressure).where(BloodPressure.user_id == current_user.id)

    # Default to lookback_days if no start_time provided
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=lookback_days)

    query = query.where(BloodPressure.timestamp >= start_time)

    if end_time:
        query = query.where(BloodPressure.timestamp <= end_time)

    query = query.order_by(BloodPressure.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    readings = result.scalars().all()
    return readings


@router.get("/readings/latest", response_model=BloodPressureResponse)
async def get_latest_blood_pressure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most recent blood pressure reading."""
    query = select(BloodPressure).where(
        BloodPressure.user_id == current_user.id
    ).order_by(BloodPressure.timestamp.desc()).limit(1)

    result = await db.execute(query)
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="No blood pressure readings found")

    return reading


@router.get("/readings/stats")
async def get_blood_pressure_statistics(
    lookback_days: int = Query(30, le=365, description="Days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get blood pressure statistics."""
    start_time = datetime.utcnow() - timedelta(days=lookback_days)

    query = select(BloodPressure).where(
        BloodPressure.user_id == current_user.id,
        BloodPressure.timestamp >= start_time
    )

    result = await db.execute(query)
    readings = result.scalars().all()

    if not readings:
        return {"message": "No blood pressure readings found in this period"}

    systolic_values = [r.systolic for r in readings]
    diastolic_values = [r.diastolic for r in readings]
    heart_rates = [r.heart_rate for r in readings if r.heart_rate]

    return {
        "period_days": lookback_days,
        "total_readings": len(readings),
        "systolic": {
            "avg": round(sum(systolic_values) / len(systolic_values), 1),
            "min": min(systolic_values),
            "max": max(systolic_values)
        },
        "diastolic": {
            "avg": round(sum(diastolic_values) / len(diastolic_values), 1),
            "min": min(diastolic_values),
            "max": max(diastolic_values)
        },
        "heart_rate": {
            "avg": round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else None,
            "min": min(heart_rates) if heart_rates else None,
            "max": max(heart_rates) if heart_rates else None
        } if heart_rates else None
    }


@router.delete("/readings/{reading_id}", status_code=204)
async def delete_blood_pressure_reading(
    reading_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a blood pressure reading."""
    query = select(BloodPressure).where(
        BloodPressure.id == reading_id,
        BloodPressure.user_id == current_user.id
    )

    result = await db.execute(query)
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="Blood pressure reading not found")

    await db.delete(reading)
    await db.flush()
    return None
