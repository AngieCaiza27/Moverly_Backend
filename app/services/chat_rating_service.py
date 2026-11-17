from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_rating import ChatMessage, Rating


async def create_message(session: AsyncSession, *, orden_id: uuid.UUID, remitente_id: uuid.UUID, mensaje: str) -> ChatMessage:
    message = ChatMessage(orden_id=orden_id, remitente_id=remitente_id, mensaje=mensaje)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def list_messages(session: AsyncSession, *, orden_id: uuid.UUID) -> list[ChatMessage]:
    result = await session.execute(select(ChatMessage).where(ChatMessage.orden_id == orden_id))
    return list(result.scalars().all())


async def create_rating(
    session: AsyncSession,
    *,
    orden_id: uuid.UUID,
    usuario_califica_id: uuid.UUID,
    usuario_calificado_id: uuid.UUID,
    puntaje: int,
    comentario: str | None,
) -> Rating:
    rating = Rating(
        orden_id=orden_id,
        usuario_califica_id=usuario_califica_id,
        usuario_calificado_id=usuario_calificado_id,
        puntaje=puntaje,
        comentario=comentario,
    )
    session.add(rating)
    await session.commit()
    await session.refresh(rating)
    return rating


