from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.driver import DriverProfileCreate


class DriverVerificationRequest(BaseModel):
    """Schema para solicitar verificación de un conductor"""
    conductor_id: uuid.UUID
    verificado: bool
    comentarios: str | None = None


class DriverVerificationOut(BaseModel):
    """Schema de respuesta para verificación de conductor"""
    conductor_id: uuid.UUID
    verificado: bool
    verificado_por: uuid.UUID
    fecha_verificacion: datetime
    comentarios: str | None = None

    class Config:
        from_attributes = True


class PendingDriverOut(BaseModel):
    """Schema para conductores pendientes de verificación"""
    usuario_id: uuid.UUID
    nombre_completo: str
    correo: str
    telefono: str | None = None
    licencia_numero: str
    licencia_categoria: str
    licencia_vigente: bool
    licencia_documento: str | None = None
    documento_respaldo: str | None = None
    verificado: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class AdminStatsOut(BaseModel):
    """Schema para estadísticas del administrador"""
    total_usuarios: int
    total_conductores: int
    conductores_verificados: int
    conductores_pendientes: int
    total_ordenes: int
    ordenes_pendientes: int
    ordenes_en_curso: int
    ordenes_completadas: int


class DocumentUploadOut(BaseModel):
    """Schema para respuesta de subida de documentos"""
    conductor_id: uuid.UUID
    tipo_documento: Literal["licencia", "respaldo"]
    url_documento: str
    subido_en: datetime

    class Config:
        from_attributes = True


class AdminCreate(BaseModel):
    correo: str
    contrasena: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)

    class Config:
        schema_extra = {
            "example": {
                "correo": "admin@example.com",
                "contrasena": "SuperSecret123",
                "first_name": "Admin",
                "last_name": "Uno"
            }
        }


class AdminCreateDriver(BaseModel):
    correo: str
    contrasena: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)
    telefono: str | None = None
    profile: DriverProfileCreate
    vehicles: list[dict] | None = None

    class Config:
        schema_extra = {
            "example": {
                "correo": "driver@example.com",
                "contrasena": "DriverPass123",
                "nombre_completo": "Juana Conductor",
                "telefono": "+59399999999",
                "profile": {
                    "licencia_numero": "ABC12345",
                    "licencia_categoria": "E",
                    "licencia_vigente": True,
                    "licencia_documento": "https://.../licencia.jpg"
                },
                "vehicles": [
                    {
                        "placa": "PST-123",
                        "tipo": "camión",
                        "capacidad_kg": 2000
                    }
                ]
            }
        }
