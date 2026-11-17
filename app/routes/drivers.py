from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import json
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
async def create_or_update_profile(
    # For multipart/form-data Swagger UI doesn't render nested models. Accept a
    # `payload` form field with a JSON string when using multipart. When the
    # client sends application/json, FastAPI will still populate this as None
    # and the JSON body will be provided directly via `payload_json` below.
    payload: str | None = Form(None),
    licencia_documento: UploadFile | None = File(None),
    documento_respaldo: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Upsert del perfil del conductor.

    Acepta JSON (application/json) con los campos de DriverProfileCreate
    y/o multipart/form-data con `licencia_documento` y/o `documento_respaldo`.
    Si se reciben archivos los guarda en `uploads/` y actualiza las rutas en
    el perfil.
    """
    from pathlib import Path
    from uuid import uuid4

    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Obtener o crear profile
    result = await session.execute(select(DriverProfile).where(DriverProfile.usuario_id == current_user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        # Crear perfil mínimo si no existe
        profile = DriverProfile(usuario_id=current_user.id)
        session.add(profile)
        await session.flush()

    # If payload is provided as form-data (string), parse it as JSON into the
    # Pydantic model. If the client sent application/json, FastAPI will have
    # placed the JSON body in the request body and we didn't declare a Body
    # parameter here, so try to detect and parse the form 'payload' only.
    payload_obj: DriverProfileCreate | None = None
    if payload:
        try:
            payload_dict = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid JSON in form field 'payload'")
        try:
            payload_obj = DriverProfileCreate(**payload_dict)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid payload: {e}")

    # If we have a parsed payload_obj, update fields from it
    if payload_obj is not None:
        profile.licencia_numero = payload_obj.licencia_numero
        profile.licencia_categoria = payload_obj.licencia_categoria
        profile.licencia_vigente = payload_obj.licencia_vigente
        # Do not overwrite document fields here unless explicitly provided in payload
        if payload_obj.licencia_documento is not None:
            profile.licencia_documento = payload_obj.licencia_documento
        if payload_obj.documento_respaldo is not None:
            profile.documento_respaldo = payload_obj.documento_respaldo

    # Helper para guardar archivo
    async def _save_file(upload: UploadFile) -> str:
        suffix = Path(upload.filename).suffix
        filename = f"{uuid4().hex}{suffix}"
        dest = upload_dir / filename
        content = await upload.read()
        dest.write_bytes(content)
        # Devolver ruta relativa que la app pueda servir (ajustar en producción)
        return f"/uploads/{filename}"

    # Guardar archivos si vienen en multipart
    if licencia_documento is not None:
        profile.licencia_documento = await _save_file(licencia_documento)
    if documento_respaldo is not None:
        profile.documento_respaldo = await _save_file(documento_respaldo)

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


@router.get("/", response_model=list[DriverProfileOut])
async def list_verified_drivers(session: AsyncSession = Depends(get_session)):
    """Listar conductores verificados públicamente.

    Devuelve los perfiles de conductor con `verificado == True`, ordenados por
    `fecha_verificacion` descendente.
    """
    result = await session.execute(select(DriverProfile).where(DriverProfile.verificado == True).order_by(DriverProfile.fecha_verificacion.desc()))
    return list(result.scalars().all())


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: uuid.UUID, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """Eliminar un vehículo propio del conductor."""
    result = await session.execute(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.conductor_id == current_user.id))
    vehicle = result.scalar_one_or_none()
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    await session.delete(vehicle)
    await session.commit()
    return None


@router.delete("/availability/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability(availability_id: int, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """Eliminar un registro de disponibilidad del conductor."""
    result = await session.execute(select(DriverAvailability).where(DriverAvailability.id == availability_id, DriverAvailability.conductor_id == current_user.id))
    availability = result.scalar_one_or_none()
    if availability is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disponibilidad no encontrada")
    await session.delete(availability)
    await session.commit()
    return None


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """Eliminar el perfil del conductor del usuario actual (no elimina al usuario)."""
    result = await session.execute(select(DriverProfile).where(DriverProfile.usuario_id == current_user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    await session.delete(profile)
    await session.commit()
    return None


