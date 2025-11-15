"""Medications endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.base import get_db
from app.models.user import User
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/medications", tags=["medications"])


@router.post("/", response_model=MedicationResponse, status_code=201)
async def create_medication(
    medication: MedicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new medication."""
    db_medication = Medication(
        user_id=current_user.id,
        **medication.model_dump()
    )
    db.add(db_medication)
    await db.flush()
    await db.refresh(db_medication)
    return db_medication


@router.get("/", response_model=List[MedicationResponse])
async def get_medications(
    active_only: bool = Query(True, description="Show only active medications"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get medications for the authenticated user."""
    query = select(Medication).where(Medication.user_id == current_user.id)

    if active_only:
        query = query.where(Medication.is_active == True)

    query = query.order_by(Medication.medication_name)

    result = await db.execute(query)
    medications = result.scalars().all()
    return medications


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific medication."""
    query = select(Medication).where(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    )

    result = await db.execute(query)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    return medication


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    medication_update: MedicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a medication."""
    query = select(Medication).where(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    )

    result = await db.execute(query)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    # Update fields
    update_data = medication_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medication, field, value)

    await db.flush()
    await db.refresh(medication)
    return medication


@router.delete("/{medication_id}", status_code=204)
async def delete_medication(
    medication_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a medication (or mark as inactive)."""
    query = select(Medication).where(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    )

    result = await db.execute(query)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    # Soft delete by marking as inactive
    medication.is_active = False
    await db.flush()
    return None
