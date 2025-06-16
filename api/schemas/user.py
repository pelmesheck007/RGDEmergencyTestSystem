from pydantic import BaseModel, EmailStr, validator
from enum import Enum
from typing import Optional
from datetime import datetime


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
    full_name: str
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.STUDENT


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None


class UserOut(UserBase):
    id: str
    role: Optional[UserRole] = None
    registration_date: datetime

    class Config:
        orm_mode = True


class UserRegister(UserCreate):
    pass

    @validator('username')
    def username_validator(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # если нужно

