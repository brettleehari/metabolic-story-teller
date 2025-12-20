"""Activity endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityResponse, status_code=201)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a physical activity (requires authentication)."""
    db_activity = Activity(
        user_id=current_user.id,
        **activity.model_dump()
    )
    db.add(db_activity)
    await db.flush()
    await db.refresh(db_activity)
    return db_activity


@router.post("/bulk", status_code=201)
async def bulk_upload_activities(
    data: ActivityBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload activity data (requires authentication)."""
    db_activities = [
        Activity(user_id=current_user.id, **activity.model_dump())
        for activity in data.activities
    ]
    db.add_all(db_activities)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_activities),
        "message": f"Successfully uploaded {len(db_activities)} activity records"
    }


@router.get("", response_model=List[ActivityResponse])
async def get_activities(
    start: Optional[datetime] = Query(None, description="Start date/time"),
    end: Optional[datetime] = Query(None, description="End date/time"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    intensity: Optional[str] = Query(None, description="Filter by intensity"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get activity data within a time range (requires authentication)."""
    query = select(Activity).where(Activity.user_id == current_user.id)

    if start:
        query = query.where(Activity.timestamp >= start)
    if end:
        query = query.where(Activity.timestamp <= end)
    if activity_type:
        query = query.where(Activity.activity_type == activity_type)
    if intensity:
        query = query.where(Activity.intensity == intensity)

    query = query.order_by(Activity.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    activities = result.scalars().all()

    return activities
