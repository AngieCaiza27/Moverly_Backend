from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import DriverAvailability, DriverProfile, Vehicle


async def upsert_profile(session: AsyncSession, *, usuario_id: uuid.UUID, licencia_numero: str, licencia_categoria: str) -> DriverProfile:
    result = await session.execute(select(DriverProfile).where(DriverProfile.usuario_id == usuario_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = DriverProfile(
            usuario_id=usuario_id,
            licencia_numero=licencia_numero,
            licencia_categoria=licencia_categoria,
        )
        session.add(profile)
    else:
        profile.licencia_numero = licencia_numero
        profile.licencia_categoria = licencia_categoria
    await session.commit()
    await session.refresh(profile)
    return profile


async def add_vehicle(session: AsyncSession, *, conductor_id: uuid.UUID, placa: str, tipo: str, capacidad_kg: int, notas: str | None) -> Vehicle:
    vehicle = Vehicle(conductor_id=conductor_id, placa=placa, tipo=tipo, capacidad_kg=capacidad_kg, notas=notas)
    session.add(vehicle)
    await session.commit()
    await session.refresh(vehicle)
    return vehicle


async def list_vehicles_by_driver(session: AsyncSession, *, conductor_id: uuid.UUID) -> list[Vehicle]:
    result = await session.execute(select(Vehicle).where(Vehicle.conductor_id == conductor_id))
    return list(result.scalars().all())


async def upsert_availability(
    session: AsyncSession,
    *,
    conductor_id: uuid.UUID,
    disponible: bool,
    zona: str | None,
    latitud: float | None,
    longitud: float | None,
) -> DriverAvailability:
    result = await session.execute(select(DriverAvailability).where(DriverAvailability.conductor_id == conductor_id))
    availability = result.scalar_one_or_none()
    if availability is None:
        availability = DriverAvailability(conductor_id=conductor_id, disponible=disponible, zona=zona, latitud=latitud, longitud=longitud)
        session.add(availability)
    else:
        availability.disponible = disponible
        availability.zona = zona
        availability.latitud = latitud
        availability.longitud = longitud
    await session.commit()
    await session.refresh(availability)
    return availability


