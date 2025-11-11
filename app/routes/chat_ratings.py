from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.chat_rating import ChatMessage, Rating
from app.schemas.chat_rating import ChatMessageCreate, ChatMessageOut, RatingCreate, RatingOut


router = APIRouter(prefix="/chat", tags=["chat"])  # keep router tag for chat messages


@router.post("/{order_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(order_id: uuid.UUID, payload: ChatMessageCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    message = ChatMessage(orden_id=order_id, remitente_id=current_user.id, mensaje=payload.mensaje)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


@router.get("/{order_id}/messages", response_model=list[ChatMessageOut])
async def list_messages(order_id: uuid.UUID, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(ChatMessage).where(ChatMessage.orden_id == order_id))
    return list(result.scalars().all())


@router.post("/{order_id}/ratings", response_model=RatingOut, status_code=status.HTTP_201_CREATED, tags=["ratings"])
async def create_rating(order_id: uuid.UUID, payload: RatingCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    rating = Rating(
        orden_id=order_id,
        usuario_califica_id=current_user.id,
        usuario_calificado_id=payload.usuario_calificado_id,
        puntaje=payload.puntaje,
        comentario=payload.comentario,
    )
    session.add(rating)
    await session.commit()
    await session.refresh(rating)
    return rating


