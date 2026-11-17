from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow)


