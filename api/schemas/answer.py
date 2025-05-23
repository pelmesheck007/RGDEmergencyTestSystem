from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskAnswerIn(BaseModel):
    task_id: str
    string_answer: Optional[str] = None
    selected_variable_ids: List[str] = []
    time_spent: Optional[int] = None

class TestAnswerIn(BaseModel):
    test_id: str
    student_id: str
    answers: List[TaskAnswerIn]

class TestAnswerOut(BaseModel):
    id: str
    test_id: str
    student_id: str
    score: float
    is_passed: bool
    class Config:
        orm_mode = True
