from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole


async def get_user_by_email(session: AsyncSession, correo: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.correo == correo))
    return result.scalar_one_or_none()


async def register_user(session: AsyncSession, correo: str, contrasena: str, first_name: str, last_name: str, rol: str) -> User:
    full_name = f"{first_name.strip()} {last_name.strip()}"
    user = User(
        correo=correo,
        contrasena_hash=hash_password(contrasena),
        nombre_completo=full_name,
        rol=UserRole(rol),
        activo=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, correo: str, contrasena: str) -> Optional[User]:
    user = await get_user_by_email(session, correo)
    if user is None or not verify_password(contrasena, user.contrasena_hash) or not user.activo:
        return None
    return user


def issue_access_token(user: User) -> str:
    return create_access_token(user.id)


