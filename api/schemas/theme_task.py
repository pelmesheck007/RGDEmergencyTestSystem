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


class ThemeCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ThemeOut(BaseModel):
    id: str
    title: str
    theme: str

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import List, Optional



class VariableAnswerCreate(BaseModel):
    string_answer: str
    truthful: bool
    explanation: Optional[str] = None
    order_number: Optional[int] = 0


class TaskCreateCustom(BaseModel):
    question: str
    interaction_type: int  # заменяет task_type
    question_details: Optional[str] = None
    difficulty_level: Optional[int] = 1
    count_variables: Optional[int] = 0
    time_limit: Optional[int] = None
    theme: Optional[str] = None
    variable_answers: Optional[List[VariableAnswerCreate]] = []


class TasksBatchCreate(BaseModel):
    test_id: str
    tasks: List[TaskCreateCustom]