# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import uuid

from sqlalchemy.orm import Session

from api.database import get_db
from api.models.user import User
from api.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from api.schemas.user import UserRegister, UserOut, LoginRequest, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    # Проверка по email
    result = db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        role="student",
        position="Проводник",
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.id})

    return {
        "access_token": access_token,
        "user": UserOut.from_orm(db_user)
    }
