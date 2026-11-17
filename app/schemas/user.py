from __future__ import annotations

import uuid
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    correo: EmailStr
    telefono: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    rol: str
    activo: bool = True


class UserCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    first_name: str
    last_name: str
    rol: str = "cliente"


class UserOut(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


