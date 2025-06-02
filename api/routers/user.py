# app/routers/users.py
import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.dependencies import get_current_user, get_db
from api.schemas import *
from api.models.user import User
from api.schemas.user import UserUpdate, UserOut, UserCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(prefix="/users", tags=["Users"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: str = Depends(require_admin), require_admin=None):
    return user_service.create_user(db, data)




@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return user_service.get_all_users(db)


@router.get("/me", response_model=UserOut)
def get_own_profile(user=Depends(get_current_user)):
    return user

@router.post("/users/me/avatar")
async def upload_avatar(file: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    file_ext = os.path.splitext(file.filename)[-1]
    if file_ext.lower() not in [".jpg", ".jpeg", ".png"]:
        return JSONResponse(status_code=400, content={"detail": "Неверный формат файла"})

    filename = f"{uuid4().hex}{file_ext}"
    file_path = f"media/avatars/{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # обновляем пользователя
    user.avatar_url = f"/{file_path}"
    db.commit()

    return {"avatar_url": user.avatar_url}

@router.put("/me", response_model=UserOut)
def update_own_profile(data: UserUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return user_service.update_user(db, user.id, data)


@router.put("/{user_id}", response_model=UserOut)
def admin_update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    deleted = user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "Deleted successfully"}


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

    @validator('username')
    def username_validator(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @validator('full_name')
    def full_name_validator(cls, v):
        if v is not None and len(v) > 256:
            raise ValueError("Full name too long")
        return v


@router.patch("/me", response_model=UserUpdate)
async def update_current_user(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Обновление данных текущего пользователя
    """
    try:
        update_data = user_data.dict(exclude_unset=True)

        # Проверка уникальности username
        if 'username' in update_data:
            existing_user = db.query(User).filter(
                User.username == update_data['username'],
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Проверка уникальности email
        if 'email' in update_data:
            existing_email = db.query(User).filter(
                User.email == update_data['email'],
                User.id != current_user.id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Обновление полей
        for field, value in update_data.items():
            setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        return {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )