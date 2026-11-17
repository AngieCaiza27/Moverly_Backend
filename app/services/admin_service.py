from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.driver import DriverProfile
from app.models.order import Order, OrderStatus


async def get_system_stats(session: AsyncSession) -> dict:
    """Obtener estadísticas generales del sistema"""
    
    # Contar usuarios por rol
    total_usuarios = await session.scalar(select(func.count(User.id)))
    total_conductores = await session.scalar(
        select(func.count(User.id)).where(User.rol == UserRole.driver)
    )
    
    # Contar conductores verificados y pendientes
    conductores_verificados = await session.scalar(
        select(func.count(DriverProfile.usuario_id)).where(DriverProfile.verificado == True)
    )
    conductores_pendientes = await session.scalar(
        select(func.count(DriverProfile.usuario_id)).where(DriverProfile.verificado == False)
    )
    
    # Contar órdenes por estado
    total_ordenes = await session.scalar(select(func.count(Order.id)))
    ordenes_pendientes = await session.scalar(
        select(func.count(Order.id)).where(Order.estado == OrderStatus.pendiente)
    )
    ordenes_en_curso = await session.scalar(
        select(func.count(Order.id)).where(Order.estado == OrderStatus.en_curso)
    )
    ordenes_completadas = await session.scalar(
        select(func.count(Order.id)).where(Order.estado == OrderStatus.completada)
    )
    
    return {
        "total_usuarios": total_usuarios or 0,
        "total_conductores": total_conductores or 0,
        "conductores_verificados": conductores_verificados or 0,
        "conductores_pendientes": conductores_pendientes or 0,
        "total_ordenes": total_ordenes or 0,
        "ordenes_pendientes": ordenes_pendientes or 0,
        "ordenes_en_curso": ordenes_en_curso or 0,
        "ordenes_completadas": ordenes_completadas or 0
    }


async def get_pending_drivers(session: AsyncSession) -> List[dict]:
    """Obtener conductores pendientes de verificación"""
    
    result = await session.execute(
        select(
            DriverProfile.usuario_id,
            User.nombre_completo,
            User.correo,
            User.telefono,
            DriverProfile.licencia_numero,
            DriverProfile.licencia_categoria,
            DriverProfile.licencia_vigente,
            DriverProfile.licencia_documento,
            DriverProfile.documento_respaldo,
            DriverProfile.verificado,
            User.creado_en
        )
        .join(User, DriverProfile.usuario_id == User.id)
        .where(DriverProfile.verificado == False)
        .order_by(User.creado_en.desc())
    )
    
    drivers = result.all()
    
    return [
        {
            "usuario_id": driver.usuario_id,
            "nombre_completo": driver.nombre_completo,
            "correo": driver.correo,
            "telefono": driver.telefono,
            "licencia_numero": driver.licencia_numero,
            "licencia_categoria": driver.licencia_categoria,
            "licencia_vigente": driver.licencia_vigente,
            "licencia_documento": driver.licencia_documento,
            "documento_respaldo": driver.documento_respaldo,
            "verificado": driver.verificado,
            "creado_en": driver.creado_en
        }
        for driver in drivers
    ]


async def verify_driver(
    session: AsyncSession,
    conductor_id: uuid.UUID,
    verificado: bool,
    verificado_por: uuid.UUID,
    comentarios: Optional[str] = None
) -> Optional[DriverProfile]:
    """Verificar o rechazar un conductor"""
    
    # Verificar que el conductor existe
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == conductor_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile is None:
        return None
    
    # Actualizar verificación
    profile.verificado = verificado
    profile.verificado_por = verificado_por
    profile.fecha_verificacion = datetime.utcnow()
    
    await session.commit()
    await session.refresh(profile)
    
    return profile


async def get_driver_profile(session: AsyncSession, driver_id: uuid.UUID) -> Optional[DriverProfile]:
    """Obtener perfil de un conductor específico"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == driver_id)
    )
    return result.scalar_one_or_none()


async def get_verified_drivers(session: AsyncSession) -> List[DriverProfile]:
    """Obtener lista de conductores verificados"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.verificado == True)
        .order_by(DriverProfile.fecha_verificacion.desc())
    )
    
    return list(result.scalars().all())


async def get_all_drivers(session: AsyncSession) -> List[dict]:
    """Obtener todos los conductores (verificados y pendientes)"""
    
    result = await session.execute(
        select(
            DriverProfile.usuario_id,
            User.nombre_completo,
            User.correo,
            User.telefono,
            DriverProfile.licencia_numero,
            DriverProfile.licencia_categoria,
            DriverProfile.licencia_vigente,
            DriverProfile.licencia_documento,
            DriverProfile.documento_respaldo,
            DriverProfile.verificado,
            User.creado_en
        )
        .join(User, DriverProfile.usuario_id == User.id)
        .order_by(User.creado_en.desc())
    )
    
    drivers = result.all()
    
    return [
        {
            "usuario_id": driver.usuario_id,
            "nombre_completo": driver.nombre_completo,
            "correo": driver.correo,
            "telefono": driver.telefono,
            "licencia_numero": driver.licencia_numero,
            "licencia_categoria": driver.licencia_categoria,
            "licencia_vigente": driver.licencia_vigente,
            "licencia_documento": driver.licencia_documento,
            "documento_respaldo": driver.documento_respaldo,
            "verificado": driver.verificado,
            "creado_en": driver.creado_en
        }
        for driver in drivers
    ]


async def update_driver_documents(
    session: AsyncSession,
    driver_id: uuid.UUID,
    licencia_documento: Optional[str] = None,
    documento_respaldo: Optional[str] = None
) -> Optional[DriverProfile]:
    """Actualizar documentos de un conductor"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == driver_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile is None:
        return None
    
    # Actualizar documentos
    if licencia_documento is not None:
        profile.licencia_documento = licencia_documento
    if documento_respaldo is not None:
        profile.documento_respaldo = documento_respaldo
    
    await session.commit()
    await session.refresh(profile)
    
    return profile


async def is_driver_verified(session: AsyncSession, driver_id: uuid.UUID) -> bool:
    """Verificar si un conductor está verificado"""
    
    result = await session.execute(
        select(DriverProfile.verificado).where(DriverProfile.usuario_id == driver_id)
    )
    verificado = result.scalar_one_or_none()
    
    return verificado is True
