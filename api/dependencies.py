# app/dependencies.py
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .database import get_db
from .models.user import User
from .services.auth import verify_token  # Теперь этот импорт будет работать


async def get_current_user(
        authorization: str = Header(default=None),
        db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.split(" ")[1]
    user_id = verify_token(token)  # Проверяем токен

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user