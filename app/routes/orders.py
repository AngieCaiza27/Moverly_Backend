from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderOut, OrderUpdateStatus


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    order = Order(
        cliente_id=current_user.id,
        estado=OrderStatus.pendiente,
        direccion_origen=payload.direccion_origen,
        lat_origen=payload.lat_origen,
        lng_origen=payload.lng_origen,
        direccion_destino=payload.direccion_destino,
        lat_destino=payload.lat_destino,
        lng_destino=payload.lng_destino,
        distancia_km=payload.distancia_km,
        tiempo_estimado_min=payload.tiempo_estimado_min,
        precio_estimado=payload.precio_estimado,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    # Return a response model with estado as its string value to satisfy
    # the Literal type used in the schema (Pydantic v2 enforces exact literals).
    return OrderOut(
        id=order.id,
        cliente_id=order.cliente_id,
        conductor_id=order.conductor_id,
        estado=order.estado.value if order.estado is not None else None,
    )


@router.get("/", response_model=list[OrderOut])
async def list_my_orders(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(select(Order).where(Order.cliente_id == current_user.id))
    orders = list(result.scalars().all())
    return [
        OrderOut(
            id=o.id,
            cliente_id=o.cliente_id,
            conductor_id=o.conductor_id,
            estado=o.estado.value if o.estado is not None else None,
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: uuid.UUID, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(Order).where(Order.id == order_id, Order.cliente_id == current_user.id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return OrderOut(
        id=order.id,
        cliente_id=order.cliente_id,
        conductor_id=order.conductor_id,
        estado=order.estado.value if order.estado is not None else None,
    )


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_status(order_id: uuid.UUID, payload: OrderUpdateStatus, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(Order).where(Order.id == order_id, Order.cliente_id == current_user.id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    order.estado = OrderStatus(payload.estado)
    await session.commit()
    await session.refresh(order)
    return OrderOut(
        id=order.id,
        cliente_id=order.cliente_id,
        conductor_id=order.conductor_id,
        estado=order.estado.value if order.estado is not None else None,
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: uuid.UUID, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await session.execute(select(Order).where(Order.id == order_id, Order.cliente_id == current_user.id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    await session.delete(order)
    await session.commit()
    return None


