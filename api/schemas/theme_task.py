from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from pydantic.schema import UUID


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

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import List, Optional

class TaskCreate(BaseModel):
    question: str
    task_type: str
    options: List[str] = Field(default_factory=list)
    correct_answers: List[str] = Field(default_factory=list)

class TasksBatchCreate(BaseModel):
    test_id: UUID
    tasks: List[TaskCreate]

class VariableAnswerData(BaseModel):
    string_answer: str
    truthful: bool
    order_number: Optional[int] = 0
    explanation: Optional[str] = None

class TaskData(BaseModel):
    question: str
    interaction_type: int
    difficulty_level: int
    time_limit: int
    theme: str
    variable_answers: Optional[List[VariableAnswerData]] = []

class CreateTasksRequest(BaseModel):
    test_id: str
    creator_id: str  # Добавили!
    tasks: List[TaskData]



class VariableAnswerCreate(BaseModel):
    string_answer: str
    truthful: bool
    order_number: Optional[int] = 0
    explanation: Optional[str] = None


class TaskCreateCustom(BaseModel):
    question: str
    interaction_type: int
    difficulty_level: Optional[int] = 1
    count_variables: Optional[int] = 0
    time_limit: Optional[int] = None
    theme: Optional[str] = None
    variable_answers: Optional[List[VariableAnswerCreate]] = []


