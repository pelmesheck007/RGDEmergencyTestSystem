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
    student_id = Column(String, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.utcnow)
    modified_time = Column(DateTime)
    time_limit = Column(Integer)
    passing_score = Column(Float)
    test_type = Column(SQLEnum(TestType), default=TestType.TRAINING)
    is_random_order = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    attempts_limit = Column(Integer)
    theme = Column(String(256))

    author_id = Column(String, ForeignKey("users.id"))
    tasks_associations = relationship("TestTask", back_populates="test", cascade="all, delete-orphan")
    test_answers = relationship("TestAnswer", back_populates="test", cascade="all, delete-orphan")

    creator = relationship("User", back_populates="created_tests", foreign_keys=[creator_id])
    author = relationship("User", back_populates="authored_tests", foreign_keys=[author_id])
    student = relationship("User", back_populates="assigned_tests", foreign_keys=[student_id])


class TestTask(Base):
    __tablename__ = 'test_tasks'

    test_id = Column(String, ForeignKey('tests.id'), primary_key=True)
    task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
    order_number = Column(Integer, default=0)
    score_weight = Column(Float, default=1.0)

    test = relationship("Test", back_populates="tasks_associations")
    task = relationship("Task", back_populates="test_associations")


class TestAnswer(Base):
    __tablename__ = 'test_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    test_id = Column(String, ForeignKey('tests.id'), nullable=False)
    start_datetime = Column(DateTime, default=datetime.utcnow)
    end_datetime = Column(DateTime)
    passing_datetime = Column(DateTime)
    score = Column(Float, nullable=False)
    max_possible_score = Column(Float, nullable=False)
    is_passed = Column(Boolean)
    attempt_number = Column(Integer, default=1)
    time_spent = Column(Integer)

    student = relationship("User", back_populates="test_answers")
    test = relationship("Test", back_populates="test_answers")
    task_answers = relationship("TaskAnswer", back_populates="test_answer", cascade="all, delete-orphan")
