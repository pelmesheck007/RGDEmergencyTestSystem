# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from sqlalchemy import select
from ..services.auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash,
)
from ..database import get_db
from ..models.user import User

router = APIRouter(tags=["auth"])
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import User
from api.schemas.user import UserRegister, UserOut
import uuid

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    user = User(
        id=str(uuid.uuid4()),
        username=data.username,
        fio=data.fio,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role="student",  # по умолчанию
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

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