"""Activity endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.base import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse

router = APIRouter(prefix="/activities", tags=["activities"])

MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("", response_model=ActivityResponse, status_code=201)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Log a physical activity."""
    db_activity = Activity(
        user_id=MOCK_USER_ID,
        **activity.model_dump()
    )
    db.add(db_activity)
    await db.flush()
    await db.refresh(db_activity)
    return db_activity
