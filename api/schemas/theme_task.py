from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ThemeTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    theme: Optional[str] = None
    order_number: Optional[int] = 0
    is_active: Optional[bool] = True


class ThemeTaskCreate(ThemeTaskBase):
    pass


class ThemeTaskUpdate(ThemeTaskBase):
    pass


class ThemeTaskOut(ThemeTaskBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
