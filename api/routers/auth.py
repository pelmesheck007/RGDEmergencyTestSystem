# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from sqlalchemy import select
from ..services.auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..database import get_db
from ..models.user import User

router = APIRouter(tags=["auth"])
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(
    login_data: LoginRequest,  # Принимаем JSON вместо формы
    db: AsyncSession = Depends(get_db),
):
    user = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = user.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}