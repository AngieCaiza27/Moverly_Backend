from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.driver import DriverAvailability, DriverProfile, Vehicle
from app.schemas.driver import (
    AvailabilityOut,
    AvailabilityUpsert,
    DriverProfileCreate,
    DriverProfileOut,
    VehicleCreate,
    VehicleOut,
)


router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post("/profile", response_model=DriverProfileOut, status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(payload: DriverProfileCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    # Upsert simple por usuario
    result = await session.execute(select(DriverProfile).where(DriverProfile.usuario_id == current_user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = DriverProfile(
            usuario_id=current_user.id,
            licencia_numero=payload.licencia_numero,
            licencia_categoria=payload.licencia_categoria,
            licencia_vigente=payload.licencia_vigente,
            licencia_documento=payload.licencia_documento,
            documento_respaldo=payload.documento_respaldo,
        )
        session.add(profile)
    else:
        profile.licencia_numero = payload.licencia_numero
        profile.licencia_categoria = payload.licencia_categoria
        profile.licencia_vigente = payload.licencia_vigente
        profile.licencia_documento = payload.licencia_documento
        profile.documento_respaldo = payload.documento_respaldo
    await session.commit()
    await session.refresh(profile)
    return profile


@router.post("/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def add_vehicle(payload: VehicleCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    vehicle = Vehicle(
        conductor_id=current_user.id,
        placa=payload.placa,
        tipo=payload.tipo,
        capacidad_kg=payload.capacidad_kg,
        documento_respaldo=payload.documento_respaldo,
    )
    session.add(vehicle)
    await session.commit()
    await session.refresh(vehicle)
    return vehicle


@router.get("/vehicles", response_model=list[VehicleOut])
async def list_my_vehicles(session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(Vehicle).where(Vehicle.conductor_id == current_user.id))
    return list(result.scalars().all())


@router.put("/availability", response_model=AvailabilityOut)
async def upsert_availability(payload: AvailabilityUpsert, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(DriverAvailability).where(DriverAvailability.conductor_id == current_user.id))
    availability = result.scalar_one_or_none()
    if availability is None:
        availability = DriverAvailability(conductor_id=current_user.id, **payload.model_dump())
        session.add(availability)
    else:
        for k, v in payload.model_dump().items():
            setattr(availability, k, v)
    await session.commit()
    await session.refresh(availability)
    return availability


