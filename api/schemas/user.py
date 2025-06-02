from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class UserBase(BaseModel):
    username: str
    fio: str
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.STUDENT


class UserUpdate(BaseModel):
    fio: Optional[str]
    avatar_url: Optional[str]


class UserOut(UserBase):
    id: str
    role: UserRole
    is_active: bool
    registration_date: datetime

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    username: str
    fio: str
    email: Optional[EmailStr]
    password: str
