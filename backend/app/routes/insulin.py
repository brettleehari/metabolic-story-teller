"""Insulin dose endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.insulin import InsulinDose
from app.schemas.insulin import InsulinDoseCreate, InsulinDoseResponse, InsulinDoseBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/insulin", tags=["insulin"])


@router.post("/doses", response_model=InsulinDoseResponse, status_code=201)
async def create_insulin_dose(
    dose: InsulinDoseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a single insulin dose."""
    db_dose = InsulinDose(
        user_id=current_user.id,
        **dose.model_dump()
    )
    db.add(db_dose)
    await db.flush()
    await db.refresh(db_dose)
    return db_dose


@router.post("/bulk", status_code=201)
async def bulk_upload_insulin_doses(
    data: InsulinDoseBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload insulin doses."""
    db_doses = [
        InsulinDose(user_id=current_user.id, **dose.model_dump())
        for dose in data.doses
    ]
    db.add_all(db_doses)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_doses),
        "start_time": db_doses[0].timestamp if db_doses else None,
        "end_time": db_doses[-1].timestamp if db_doses else None,
    }


@router.get("/doses", response_model=List[InsulinDoseResponse])
async def get_insulin_doses(
    start_time: Optional[datetime] = Query(None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter until this timestamp"),
    insulin_type: Optional[str] = Query(None, description="Filter by type (basal, bolus, correction)"),
    lookback_hours: int = Query(24, le=720, description="Hours to look back (default 24)"),
    limit: int = Query(1000, le=10000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insulin doses for the authenticated user."""
    query = select(InsulinDose).where(InsulinDose.user_id == current_user.id)

    # Default to lookback_hours if no start_time provided
    if not start_time:
        start_time = datetime.utcnow() - timedelta(hours=lookback_hours)

    query = query.where(InsulinDose.timestamp >= start_time)

    if end_time:
        query = query.where(InsulinDose.timestamp <= end_time)

    if insulin_type:
        query = query.where(InsulinDose.insulin_type == insulin_type)

    query = query.order_by(InsulinDose.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    doses = result.scalars().all()
    return doses


@router.get("/doses/stats")
async def get_insulin_statistics(
    lookback_days: int = Query(7, le=90, description="Days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insulin dosing statistics."""
    start_time = datetime.utcnow() - timedelta(days=lookback_days)

    query = select(InsulinDose).where(
        InsulinDose.user_id == current_user.id,
        InsulinDose.timestamp >= start_time
    )

    result = await db.execute(query)
    doses = result.scalars().all()

    if not doses:
        return {"message": "No insulin doses found in this period"}

    # Calculate statistics
    basal_doses = [d for d in doses if d.insulin_type == 'basal']
    bolus_doses = [d for d in doses if d.insulin_type == 'bolus']
    correction_doses = [d for d in doses if d.insulin_type == 'correction']

    total_basal = sum(float(d.dose_units) for d in basal_doses)
    total_bolus = sum(float(d.dose_units) for d in bolus_doses)
    total_correction = sum(float(d.dose_units) for d in correction_doses)
    total_insulin = total_basal + total_bolus + total_correction

    return {
        "period_days": lookback_days,
        "total_doses": len(doses),
        "total_insulin_units": round(total_insulin, 2),
        "avg_daily_insulin": round(total_insulin / lookback_days, 2),
        "basal": {
            "count": len(basal_doses),
            "total_units": round(total_basal, 2),
            "avg_per_dose": round(total_basal / len(basal_doses), 2) if basal_doses else 0
        },
        "bolus": {
            "count": len(bolus_doses),
            "total_units": round(total_bolus, 2),
            "avg_per_dose": round(total_bolus / len(bolus_doses), 2) if bolus_doses else 0
        },
        "correction": {
            "count": len(correction_doses),
            "total_units": round(total_correction, 2),
            "avg_per_dose": round(total_correction / len(correction_doses), 2) if correction_doses else 0
        }
    }


@router.delete("/doses/{dose_id}", status_code=204)
async def delete_insulin_dose(
    dose_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an insulin dose record."""
    query = select(InsulinDose).where(
        InsulinDose.id == dose_id,
        InsulinDose.user_id == current_user.id
    )

    result = await db.execute(query)
    dose = result.scalar_one_or_none()

    if not dose:
        raise HTTPException(status_code=404, detail="Insulin dose not found")

    await db.delete(dose)
    await db.flush()
    return None
