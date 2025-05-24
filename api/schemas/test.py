# schemas/test.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime
from typing import List

class TestType(str, Enum):
    TRAINING = "training"
    CERTIFICATION = "certification"


class TestBase(BaseModel):
    test_name: Optional[str]
    description: Optional[str]
    creator_id: Optional[str]
    student_id: Optional[str]
    time_limit: Optional[int]
    passing_score: Optional[float]
    test_type: Optional[TestType]
    is_random_order: Optional[bool]
    is_active: Optional[bool]
    attempts_limit: Optional[int]
    theme: Optional[str]
    author_id: Optional[str]



class TestUpdate(TestBase):
    pass


class TestOut(TestBase):
    id: str
    creation_time: Optional[datetime]
    modified_time: Optional[datetime]

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


class TestCreate(BaseModel):
    test_name: str
    description: str
    time_limit: int
    passing_score: int
    theme_id: str
    attempts_limit: int

