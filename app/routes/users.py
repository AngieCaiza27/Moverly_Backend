from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.user import UserOut


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


