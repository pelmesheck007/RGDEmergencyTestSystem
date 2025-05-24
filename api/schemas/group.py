# schemas/group.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudyGroupOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class StudyGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class StudyGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
