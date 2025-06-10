from .base import Base
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime,
    ForeignKey, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
import uuid
from datetime import datetime
from enum import Enum


def generate_uuid():
    return str(uuid.uuid4())


class TestType(str, Enum):
    TRAINING = "training"
    CERTIFICATION = "certification"


class Test(Base):
    __tablename__ = 'tests'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_name = Column(String(256), nullable=False)
    description = Column(Text)
    creator_id = Column(String, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.utcnow)
    modified_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    time_limit = Column(Integer)
    passing_score = Column(Float)
    test_type = Column(SQLEnum(TestType), default=TestType.TRAINING)

    theme_id = Column(String, ForeignKey('theme.id'))

    # Прямая связь с Task
    tasks = relationship("Task", back_populates="test", cascade="all, delete-orphan")
    test_answers = relationship("TestAnswer", back_populates="test", cascade="all, delete-orphan")

    creator = relationship("User", back_populates="created_tests")
    theme = relationship("Theme", back_populates="tests")
    assigned_groups = relationship("GroupAssignedTest", back_populates="test", cascade="all, delete-orphan")

class Theme(Base):
    __tablename__ = 'theme'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    tests = relationship("Test", back_populates="theme")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_id = Column(String, ForeignKey('tests.id'), nullable=False)
    question = Column(Text, nullable=False)
    question_details = Column(Text)
    interaction_type = Column(Integer, nullable=False)  # 1 - текст, 2 - множественный выбор
    difficulty_level = Column(Integer, default=1)

    test = relationship("Test", back_populates="tasks")
    variable_answers = relationship("VariableAnswer", back_populates="task", cascade="all, delete-orphan")
    answers = relationship("TaskAnswer", back_populates="task", cascade="all, delete-orphan")


class VariableAnswer(Base):
    __tablename__ = 'variable_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    string_answer = Column(Text, nullable=False)
    truthful = Column(Boolean, nullable=False)
    order_number = Column(Integer, default=0)
    explanation = Column(Text)

    task = relationship("Task", back_populates="variable_answers")
    selected_in_answers = relationship(
        "TaskAnswerVariableAnswer",
        back_populates="variable_answer",
        cascade="all, delete-orphan"
    )


class TestAnswer(Base):
    __tablename__ = 'test_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    test_id = Column(String, ForeignKey('tests.id'), nullable=False)
    start_datetime = Column(DateTime, default=datetime.utcnow)
    end_datetime = Column(DateTime)
    score = Column(Float, nullable=False)
    is_passed = Column(Boolean)

    test = relationship("Test", back_populates="test_answers")
    student = relationship("User", back_populates="test_answers")  # <-- добавь сюда!
    task_answers = relationship("TaskAnswer", back_populates="test_answer", cascade="all, delete-orphan")


class TaskAnswer(Base):
    __tablename__ = 'task_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_answer_id = Column(String, ForeignKey('test_answers.id'), nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)

    string_answer = Column(Text)  # для текстовых ответов
    is_correct = Column(Boolean)
    score = Column(Float)
    answer_date = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Integer)

    test_answer = relationship("TestAnswer", back_populates="task_answers")
    task = relationship("Task", back_populates="answers")
    student = relationship("User", back_populates="task_answers")
    selected_variable_answers = relationship(
        "TaskAnswerVariableAnswer",
        back_populates="task_answer",
        cascade="all, delete-orphan"
    )


class TaskAnswerVariableAnswer(Base):
    __tablename__ = 'task_answer_variable_answers'

    task_answer_id = Column(String, ForeignKey('task_answers.id'), primary_key=True)
    variable_answer_id = Column(String, ForeignKey('variable_answers.id'), primary_key=True)

    task_answer = relationship("TaskAnswer", back_populates="selected_variable_answers")
    variable_answer = relationship("VariableAnswer", back_populates="selected_in_answers")



