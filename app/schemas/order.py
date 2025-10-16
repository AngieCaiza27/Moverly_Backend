from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel


OrderStatusLiteral = Literal["pendiente", "aceptada", "en_curso", "completada", "cancelada"]


class OrderCreate(BaseModel):
    direccion_origen: str
    lat_origen: float
    lng_origen: float
    direccion_destino: str
    lat_destino: float
    lng_destino: float
    distancia_km: float | None = None
    tiempo_estimado_min: int | None = None
    precio_estimado: float | None = None


class OrderUpdateStatus(BaseModel):
    estado: OrderStatusLiteral


class OrderOut(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID
    conductor_id: uuid.UUID | None = None
    estado: OrderStatusLiteral

    class Config:
        from_attributes = True


