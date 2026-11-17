from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Index, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, Enum):
    client = "cliente"
    driver = "conductor"
    admin = "admin"


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(32), nullable=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    # Store using the PostgreSQL ENUM 'user_role' and map the Python
    # Enum to its .value (Spanish strings) so DB receives 'cliente',
    # 'conductor', 'admin' rather than the Python names.
    rol: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", values_callable=lambda enum: [e.value for e in enum])
    )
    nombre_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # relationships minimal for MVP
    # orders as client/driver set up in order model

    __table_args__ = (
        Index("ix_usuarios_correo", "correo", unique=True),
    )


