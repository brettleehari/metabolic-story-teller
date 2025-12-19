"""Sleep data endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.sleep import SleepData
from app.schemas.sleep import SleepDataCreate, SleepDataResponse, SleepBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/sleep", tags=["sleep"])


@router.post("", response_model=SleepDataResponse, status_code=201)
async def create_sleep_data(
    sleep: SleepDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a sleep session (requires authentication)."""
    db_sleep = SleepData(
        user_id=current_user.id,
        **sleep.model_dump()
    )
    db.add(db_sleep)
    await db.flush()
    await db.refresh(db_sleep)
    return db_sleep


@router.post("/bulk", status_code=201)
async def bulk_upload_sleep(
    data: SleepBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload sleep data (requires authentication)."""
    db_sleep_records = [
        SleepData(user_id=current_user.id, **sleep.model_dump())
        for sleep in data.sleep_records
    ]
    db.add_all(db_sleep_records)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_sleep_records),
        "message": f"Successfully uploaded {len(db_sleep_records)} sleep records"
    }


@router.get("", response_model=List[SleepDataResponse])
async def get_sleep_data(
    start: Optional[datetime] = Query(None, description="Start date/time"),
    end: Optional[datetime] = Query(None, description="End date/time"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sleep data within a time range (requires authentication)."""
    query = select(SleepData).where(SleepData.user_id == current_user.id)

    if start:
        query = query.where(SleepData.sleep_start >= start)
    if end:
        query = query.where(SleepData.sleep_end <= end)

    query = query.order_by(SleepData.sleep_start.desc()).limit(limit)

    result = await db.execute(query)
    sleep_records = result.scalars().all()

    return sleep_records
