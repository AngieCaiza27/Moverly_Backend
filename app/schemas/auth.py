from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=6)
    nombre_completo: str = Field(min_length=1, max_length=255)
    rol: Literal["cliente", "conductor", "admin"] = "cliente"


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


