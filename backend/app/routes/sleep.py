"""Sleep data endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.base import get_db
from app.models.sleep import SleepData
from app.schemas.sleep import SleepDataCreate, SleepDataResponse

router = APIRouter(prefix="/sleep", tags=["sleep"])

MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("", response_model=SleepDataResponse, status_code=201)
async def create_sleep_data(
    sleep: SleepDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Log a sleep session."""
    db_sleep = SleepData(
        user_id=MOCK_USER_ID,
        **sleep.model_dump()
    )
    db.add(db_sleep)
    await db.flush()
    await db.refresh(db_sleep)
    return db_sleep
