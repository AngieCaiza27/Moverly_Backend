from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DECIMAL, Index, Integer, SmallInteger, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChatMessage(Base):
    __tablename__ = "mensajes_chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes.id"), nullable=False)
    remitente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    mensaje: Mapped[str] = mapped_column(String, nullable=False)
    enviado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_chat_orden", "orden_id"),
    )


class Rating(Base):
    __tablename__ = "calificaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ordenes.id"), nullable=False)
    usuario_califica_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    usuario_calificado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    puntaje: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comentario: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_rating_usuario_calificado", "usuario_calificado_id"),
        Index("ix_rating_orden_usuario", "orden_id", "usuario_califica_id", unique=True),  # Evita calificaciones duplicadas
    )


