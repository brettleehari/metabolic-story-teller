"""Meal endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.base import get_db
from app.models.meal import Meal
from app.schemas.meal import MealCreate, MealResponse

router = APIRouter(prefix="/meals", tags=["meals"])

MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("", response_model=MealResponse, status_code=201)
async def create_meal(
    meal: MealCreate,
    db: AsyncSession = Depends(get_db)
):
    """Log a meal."""
    db_meal = Meal(
        user_id=MOCK_USER_ID,
        **meal.model_dump()
    )
    db.add(db_meal)
    await db.flush()
    await db.refresh(db_meal)
    return db_meal
