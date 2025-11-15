"""HbA1c tracking endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.hba1c import HbA1c
from app.schemas.hba1c import HbA1cCreate, HbA1cResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/hba1c", tags=["hba1c"])


@router.post("/", response_model=HbA1cResponse, status_code=201)
async def create_hba1c_reading(
    reading: HbA1cCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new HbA1c reading."""
    db_reading = HbA1c(
        user_id=current_user.id,
        **reading.model_dump()
    )
    db.add(db_reading)
    await db.flush()
    await db.refresh(db_reading)
    return db_reading


@router.get("/", response_model=List[HbA1cResponse])
async def get_hba1c_readings(
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    limit: int = Query(100, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get HbA1c readings for the authenticated user."""
    query = select(HbA1c).where(HbA1c.user_id == current_user.id)

    if start_date:
        query = query.where(HbA1c.test_date >= start_date)
    if end_date:
        query = query.where(HbA1c.test_date <= end_date)

    query = query.order_by(HbA1c.test_date.desc()).limit(limit)

    result = await db.execute(query)
    readings = result.scalars().all()
    return readings


@router.get("/latest", response_model=HbA1cResponse)
async def get_latest_hba1c(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most recent HbA1c reading."""
    query = select(HbA1c).where(
        HbA1c.user_id == current_user.id
    ).order_by(HbA1c.test_date.desc()).limit(1)

    result = await db.execute(query)
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="No HbA1c readings found")

    return reading


@router.delete("/{reading_id}", status_code=204)
async def delete_hba1c_reading(
    reading_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an HbA1c reading."""
    query = select(HbA1c).where(
        HbA1c.id == reading_id,
        HbA1c.user_id == current_user.id
    )

    result = await db.execute(query)
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="HbA1c reading not found")

    await db.delete(reading)
    await db.flush()
    return None
