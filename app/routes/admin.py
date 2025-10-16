from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.user import User, UserRole
from app.models.driver import DriverProfile
from app.models.order import Order, OrderStatus
from app.schemas.driver import DriverProfileOut
from app.schemas.admin import (
    DriverVerificationRequest,
    DriverVerificationOut,
    PendingDriverOut,
    AdminStatsOut,
    DocumentUploadOut
)

router = APIRouter(prefix="/admin", tags=["admin"])


async def verify_admin(current_user=Depends(get_current_user)):
    """Verificar que el usuario actual es administrador"""
    if current_user.rol != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta funcionalidad"
        )
    return current_user


@router.get("/stats", response_model=AdminStatsOut)
async def get_admin_stats(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
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
    
    return AdminStatsOut(
        total_usuarios=total_usuarios or 0,
        total_conductores=total_conductores or 0,
        conductores_verificados=conductores_verificados or 0,
        conductores_pendientes=conductores_pendientes or 0,
        total_ordenes=total_ordenes or 0,
        ordenes_pendientes=ordenes_pendientes or 0,
        ordenes_en_curso=ordenes_en_curso or 0,
        ordenes_completadas=ordenes_completadas or 0
    )


@router.get("/drivers/pending", response_model=List[PendingDriverOut])
async def get_pending_drivers(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
    """Obtener lista de conductores pendientes de verificación"""
    
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
        PendingDriverOut(
            usuario_id=driver.usuario_id,
            nombre_completo=driver.nombre_completo,
            correo=driver.correo,
            telefono=driver.telefono,
            licencia_numero=driver.licencia_numero,
            licencia_categoria=driver.licencia_categoria,
            licencia_vigente=driver.licencia_vigente,
            licencia_documento=driver.licencia_documento,
            documento_respaldo=driver.documento_respaldo,
            verificado=driver.verificado,
            creado_en=driver.creado_en
        )
        for driver in drivers
    ]


@router.post("/drivers/verify", response_model=DriverVerificationOut)
async def verify_driver(
    payload: DriverVerificationRequest,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
    """Verificar o rechazar un conductor"""
    
    # Verificar que el conductor existe
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == payload.conductor_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    # Actualizar verificación
    profile.verificado = payload.verificado
    profile.verificado_por = current_user.id
    profile.fecha_verificacion = datetime.utcnow()
    
    await session.commit()
    await session.refresh(profile)
    
    return DriverVerificationOut(
        conductor_id=profile.usuario_id,
        verificado=profile.verificado,
        verificado_por=current_user.id,
        fecha_verificacion=profile.fecha_verificacion,
        comentarios=payload.comentarios
    )


@router.get("/drivers/{driver_id}/profile", response_model=DriverProfileOut)
async def get_driver_profile(
    driver_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
    """Obtener perfil detallado de un conductor específico"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == driver_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    return profile


@router.get("/drivers/verified", response_model=List[DriverProfileOut])
async def get_verified_drivers(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
    """Obtener lista de conductores verificados"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.verificado == True)
        .order_by(DriverProfile.fecha_verificacion.desc())
    )
    
    return list(result.scalars().all())


@router.get("/drivers/all", response_model=List[PendingDriverOut])
async def get_all_drivers(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
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
        PendingDriverOut(
            usuario_id=driver.usuario_id,
            nombre_completo=driver.nombre_completo,
            correo=driver.correo,
            telefono=driver.telefono,
            licencia_numero=driver.licencia_numero,
            licencia_categoria=driver.licencia_categoria,
            licencia_vigente=driver.licencia_vigente,
            licencia_documento=driver.licencia_documento,
            documento_respaldo=driver.documento_respaldo,
            verificado=driver.verificado,
            creado_en=driver.creado_en
        )
        for driver in drivers
    ]


@router.put("/drivers/{driver_id}/documents", response_model=DocumentUploadOut)
async def update_driver_documents(
    driver_id: uuid.UUID,
    licencia_documento: str | None = None,
    documento_respaldo: str | None = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(verify_admin)
):
    """Actualizar documentos de un conductor (solo admin puede hacer esto)"""
    
    result = await session.execute(
        select(DriverProfile).where(DriverProfile.usuario_id == driver_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conductor no encontrado"
        )
    
    # Actualizar documentos
    if licencia_documento is not None:
        profile.licencia_documento = licencia_documento
    if documento_respaldo is not None:
        profile.documento_respaldo = documento_respaldo
    
    await session.commit()
    await session.refresh(profile)
    
    return DocumentUploadOut(
        conductor_id=profile.usuario_id,
        tipo_documento="ambos" if licencia_documento and documento_respaldo else ("licencia" if licencia_documento else "respaldo"),
        url_documento=profile.licencia_documento or profile.documento_respaldo,
        subido_en=datetime.utcnow()
    )
