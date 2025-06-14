from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime


class TestType(str, Enum):
    TRAINING = "training"
    CERTIFICATION = "certification"


class TestBase(BaseModel):
    test_name: Optional[str]
    description: Optional[str]
    creator_id: Optional[str]
    time_limit: Optional[int]
    passing_score: Optional[float]
    test_type: Optional[TestType] = TestType.TRAINING
    theme_id: Optional[str]


class TestCreate(TestBase):
    test_name: str
    description: str
    time_limit: int
    passing_score: int
    theme_id: str

class TestUpdate(TestBase):
    pass


class ThemeOut(BaseModel):
    id: str
    title: Optional[str] = None

    class Config:
        orm_mode = True


class TestOut(BaseModel):
    id: str
    test_name: str
    description: Optional[str] = None
    time_limit: Optional[int] = None
    passing_score: Optional[float] = None
    theme: Optional[ThemeOut] = None
    creation_time: datetime  # <--- имя поля, как в SQLAlchemy-модели!

    class Config:
        orm_mode = True

class AnswerOut(BaseModel):
    id: str
    text: str

class QuestionOut(BaseModel):
    id: str
    text: str
    answers: List[AnswerOut]


class VariableAnswerCreate(BaseModel):
    string_answer: str
    truthful: bool


class TaskCreate(BaseModel):
    question: str
    interaction_type: int
    time_limit: int
    difficulty_level: int
    theme: str
    variable_answers: List[VariableAnswerCreate]
