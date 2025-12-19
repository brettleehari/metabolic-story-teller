"""Meal endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.meal import Meal
from app.schemas.meal import MealCreate, MealResponse, MealBulkUpload
from app.dependencies import get_current_user

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("", response_model=MealResponse, status_code=201)
async def create_meal(
    meal: MealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a meal (requires authentication)."""
    db_meal = Meal(
        user_id=current_user.id,
        **meal.model_dump()
    )
    db.add(db_meal)
    await db.flush()
    await db.refresh(db_meal)
    return db_meal


@router.post("/bulk", status_code=201)
async def bulk_upload_meals(
    data: MealBulkUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload meal data (requires authentication)."""
    db_meals = [
        Meal(user_id=current_user.id, **meal.model_dump())
        for meal in data.meals
    ]
    db.add_all(db_meals)
    await db.flush()

    return {
        "status": "success",
        "records_created": len(db_meals),
        "message": f"Successfully uploaded {len(db_meals)} meal records"
    }


@router.get("", response_model=List[MealResponse])
async def get_meals(
    start: Optional[datetime] = Query(None, description="Start date/time"),
    end: Optional[datetime] = Query(None, description="End date/time"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meal data within a time range (requires authentication)."""
    query = select(Meal).where(Meal.user_id == current_user.id)

    if start:
        query = query.where(Meal.timestamp >= start)
    if end:
        query = query.where(Meal.timestamp <= end)
    if meal_type:
        query = query.where(Meal.meal_type == meal_type)

    query = query.order_by(Meal.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    meals = result.scalars().all()

    return meals
