from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScenarioTestBase(BaseModel):
    title: str
    description: Optional[str] = None


class ScenarioTestCreate(ScenarioTestBase):
    pass


class ThemeOut(BaseModel):
    id: str
    title: Optional[str] = None

    class Config:
        orm_mode = True


class ScenarioTestOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    time_limit: Optional[int] = None
    theme: Optional[ThemeOut] = None
    creation_time: datetime

    class Config:
        orm_mode = True

class ScenarioChoiceOut(BaseModel):
    id: str
    choice_text: str
    next_step_id: Optional[str]
    is_critical_error: bool

    class Config:
        orm_mode = True


class ScenarioStepOut(BaseModel):
    id: str
    step_text: str
    is_final: bool
    timeout_sec: Optional[int]
    choices: List[ScenarioChoiceOut]

    class Config:
        orm_mode = True


class ScenarioLogCreate(BaseModel):
    user_id: str
    step_id: str
    choice_id: str
    time_taken: Optional[int] = 0
    is_error: bool = False

