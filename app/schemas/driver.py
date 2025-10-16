from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel


class DriverProfileCreate(BaseModel):
    licencia_numero: str
    licencia_categoria: str = "E"  # Solo tipo E
    licencia_vigente: bool = False
    licencia_documento: str | None = None  # URL del archivo escaneado
    documento_respaldo: str | None = None  # Certificado de cooperativa


class DriverProfileOut(BaseModel):
    usuario_id: uuid.UUID
    licencia_numero: str
    licencia_categoria: str
    licencia_vigente: bool
    licencia_documento: str | None = None
    documento_respaldo: str | None = None
    verificado: bool
    verificado_por: uuid.UUID | None = None
    fecha_verificacion: datetime | None = None
    promedio_calificacion: float
    total_calificaciones: int

    class Config:
        from_attributes = True


class VehicleCreate(BaseModel):
    placa: str
    tipo: str = "camión"
    capacidad_kg: int
    documento_respaldo: str | None = None  # Matrícula o certificado de propiedad


class VehicleOut(BaseModel):
    id: uuid.UUID
    conductor_id: uuid.UUID
    placa: str
    tipo: str
    capacidad_kg: int
    documento_respaldo: str | None = None
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class AvailabilityUpsert(BaseModel):
    disponible: bool
    zona: str | None = None
    latitud: float | None = None
    longitud: float | None = None


class AvailabilityOut(AvailabilityUpsert):
    id: int
    conductor_id: uuid.UUID

    class Config:
        from_attributes = True


