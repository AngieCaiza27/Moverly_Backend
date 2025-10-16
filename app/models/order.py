from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DECIMAL, Enum as SAEnum, ForeignKey, Integer, String, Index
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class OrderStatus(str, Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    en_curso = "en_curso"
    completada = "completada"
    cancelada = "cancelada"


class Order(Base):
    __tablename__ = "ordenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    conductor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    estado: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.pendiente)

    direccion_origen: Mapped[str] = mapped_column(String, nullable=False)
    lat_origen: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    lng_origen: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    direccion_destino: Mapped[str] = mapped_column(String, nullable=False)
    lat_destino: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    lng_destino: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    distancia_km: Mapped[float | None] = mapped_column(DECIMAL(8, 2), nullable=True)
    tiempo_estimado_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precio_estimado: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)

    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_ordenes_estado", "estado"),
        Index("ix_ordenes_cliente", "cliente_id"),
        Index("ix_ordenes_conductor", "conductor_id"),
    )


class OrderEventOrigin(str, Enum):
    cliente = "cliente"
    conductor = "conductor"
    admin = "admin"
    sistema = "sistema"


class OrderEvent(Base):
    __tablename__ = "eventos_orden"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes.id"), nullable=False)
    tipo_evento: Mapped[str] = mapped_column(String, nullable=False)
    usuario_actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    origen: Mapped[OrderEventOrigin] = mapped_column(SAEnum(OrderEventOrigin), default=OrderEventOrigin.sistema)
    detalles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_eventos_orden_id", "orden_id"),
        Index("ix_eventos_usuario_actor", "usuario_actor_id"),
    )


