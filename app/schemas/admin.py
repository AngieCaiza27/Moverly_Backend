from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


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
