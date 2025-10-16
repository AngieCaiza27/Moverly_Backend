from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.correo == payload.correo))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    user = User(
        correo=payload.correo,
        contrasena_hash=hash_password(payload.contrasena),
        nombre_completo=payload.nombre_completo,
        rol=UserRole(payload.rol),
        activo=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=60 * 60 * 24)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.correo == payload.correo))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.contrasena, user.contrasena_hash):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=60 * 60 * 24)


@router.post("/token", response_model=TokenResponse)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    """Endpoint compatible con OAuth2 password flow (acepta form data) usado por Swagger UI."""
    result = await session.execute(select(User).where(User.correo == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.contrasena_hash):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=60 * 60 * 24)


