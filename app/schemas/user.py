from __future__ import annotations

import uuid
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    correo: EmailStr
    telefono: str | None = None
    nombre_completo: str
    rol: str
    activo: bool = True


class UserCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    nombre_completo: str
    rol: str = "cliente"


class UserOut(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


