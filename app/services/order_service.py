from __future__ import annotations

import uuid
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus


async def create_order(
    session: AsyncSession,
    *,
    cliente_id: uuid.UUID,
    direccion_origen: str | None,
    lat_origen: float | None,
    lng_origen: float | None,
    direccion_destino: str | None,
    lat_destino: float | None,
    lng_destino: float | None,
    distancia_km: float | None,
    tiempo_estimado_min: int | None,
    precio_estimado: float | None,
) -> Order:
    order = Order(
        cliente_id=cliente_id,
        estado=OrderStatus.pendiente,
        direccion_origen=direccion_origen,
        lat_origen=lat_origen,
        lng_origen=lng_origen,
        direccion_destino=direccion_destino,
        lat_destino=lat_destino,
        lng_destino=lng_destino,
        distancia_km=distancia_km,
        tiempo_estimado_min=tiempo_estimado_min,
        precio_estimado=precio_estimado,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def list_orders_for_client(session: AsyncSession, *, cliente_id: uuid.UUID) -> list[Order]:
    result = await session.execute(select(Order).where(Order.cliente_id == cliente_id))
    return list(result.scalars().all())


async def get_order_for_client(session: AsyncSession, *, order_id: uuid.UUID, cliente_id: uuid.UUID) -> Optional[Order]:
    result = await session.execute(select(Order).where(Order.id == order_id, Order.cliente_id == cliente_id))
    return result.scalar_one_or_none()


async def update_order_status(session: AsyncSession, *, order: Order, estado: str) -> Order:
    order.estado = OrderStatus(estado)
    await session.commit()
    await session.refresh(order)
    return order


async def delete_order(session: AsyncSession, *, order: Order) -> None:
    await session.delete(order)
    await session.commit()


