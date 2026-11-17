from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=6)
    # Split name to first + last for better normalization
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)
    # Do not expose 'admin' as a valid value for public registration.
    # Only allow 'cliente' or 'conductor' here; admins must be created
    # by an existing privileged user or via a protected admin flow.
    rol: Literal["cliente", "conductor"] = "cliente"


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


