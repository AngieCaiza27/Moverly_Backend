from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    mensaje: str = Field(min_length=1)


class ChatMessageOut(BaseModel):
    id: int
    orden_id: uuid.UUID
    remitente_id: uuid.UUID
    mensaje: str

    class Config:
        from_attributes = True


class RatingCreate(BaseModel):
    usuario_calificado_id: uuid.UUID
    puntaje: int = Field(ge=1, le=5)
    comentario: str | None = None


class RatingOut(BaseModel):
    id: int
    orden_id: uuid.UUID
    usuario_califica_id: uuid.UUID
    usuario_calificado_id: uuid.UUID
    puntaje: int
    comentario: str | None = None

    class Config:
        from_attributes = True


