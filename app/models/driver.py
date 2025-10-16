from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DECIMAL, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DriverProfile(Base):
    __tablename__ = "perfil_conductor"

    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), primary_key=True)
    licencia_numero: Mapped[str] = mapped_column(String, nullable=False)
    licencia_categoria: Mapped[str] = mapped_column(String, nullable=False)  # Solo tipo E
    licencia_vigente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    licencia_documento: Mapped[str | None] = mapped_column(String, nullable=True)  # URL del archivo escaneado
    documento_respaldo: Mapped[str | None] = mapped_column(String, nullable=True)  # Certificado de cooperativa
    verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verificado_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_verificacion: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    promedio_calificacion: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.00, nullable=False)
    total_calificaciones: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Vehicle(Base):
    __tablename__ = "vehiculos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conductor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    placa: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False, default="camión")
    capacidad_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    documento_respaldo: Mapped[str | None] = mapped_column(String, nullable=True)  # Matrícula o certificado de propiedad
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_vehiculos_conductor", "conductor_id"),
    )


class DriverAvailability(Base):
    __tablename__ = "disponibilidad_conductor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conductor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    zona: Mapped[str | None] = mapped_column(String, nullable=True)
    latitud: Mapped[float | None] = mapped_column(DECIMAL(9, 6), nullable=True)
    longitud: Mapped[float | None] = mapped_column(DECIMAL(9, 6), nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_disp_conductor", "conductor_id"),
        Index("ix_disp_zona", "zona"),
    )


