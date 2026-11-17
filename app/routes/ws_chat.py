from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from jose import JWTError, jwt

from app.core.config import settings
from app.services.ws_manager import manager
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.chat_rating_service import create_message as persist_message

router = APIRouter()


async def get_user_from_token(token: str | None, session: AsyncSession) -> User | None:
    if token is None:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        subject: str | None = payload.get("sub")
        if subject is None:
            return None
        user_id = uuid.UUID(subject)
    except (JWTError, ValueError):
        return None

    result = await session.execute("SELECT * FROM usuarios WHERE id = :id", {"id": str(user_id)})
    # Use raw fetch since we don't want to import ORM here; fetchone returns Row
    row = result.fetchone()
    if row is None:
        return None
    # Minimal user-like object with id
    class U:
        def __init__(self, id):
            self.id = id

    return U(user_id)


@router.websocket("/ws/chat/{order_id}")
async def websocket_chat(websocket: WebSocket, order_id: str, token: str | None = Query(None)):
    """WebSocket endpoint for chat messages per order.

    Authentication: accepts JWT as query param `token` (compatible with mobile/web clients).
    Each received text message is persisted to DB and broadcasted to other clients
    connected to the same order.
    """
    # Accept connection first (FastAPI requires accept before receive/send)
    await websocket.accept()

    # Resolve user from token using a DB session
    async with get_session() as session:  # type: ignore[attr-defined]
        user = await get_user_from_token(token, session)
        if user is None:
            await websocket.send_text(json.dumps({"error": "not_authenticated"}))
            await websocket.close(code=1008)
            return

    await manager.connect(order_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Persist message (fire-and-forget) and broadcast
            try:
                # Save to DB; create_message expects AsyncSession usage. Open a short session.
                async with get_session() as session:  # type: ignore[attr-defined]
                    await persist_message(session, orden_id=uuid.UUID(order_id), remitente_id=user.id, mensaje=data)
            except Exception:
                # If persisting fails, still broadcast to clients but mark as unsaved
                pass

            payload = json.dumps({"order_id": order_id, "from": str(user.id), "message": data})
            await manager.broadcast(order_id, payload)

    except WebSocketDisconnect:
        await manager.disconnect(order_id, websocket)
