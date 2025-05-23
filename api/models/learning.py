
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
import uuid

from .base import Base
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

def generate_uuid():
    return str(uuid.uuid4())

class TaskInteractionType(Enum):
    SINGLE_ANSWER = 1
    MULTIPLE_ANSWER = 2
    TEXT_ANSWER = 3
    # Add more types as needed

class TestType(Enum):
    TRAINING = 0
    CERTIFICATION = 1

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    question_details = Column(Text)
    interaction_type = Column(Integer, nullable=False)  # Using TaskInteractionType enum values
    creator_id = Column(String, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    difficulty_level = Column(Integer, default=1)
    count_variables = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    time_limit = Column(Integer)  # in seconds

    # Relationships
    creator = relationship("User")
    variable_answers = relationship("VariableAnswer", back_populates="task", cascade="all, delete-orphan")
    theme_associations = relationship("TaskThemeTask", back_populates="task")
    test_associations = relationship("TestTask", back_populates="task")
    answers = relationship("TaskAnswer", back_populates="task")

class VariableAnswer(Base):
    __tablename__ = 'variable_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    string_answer = Column(Text, nullable=False)
    truthful = Column(Boolean, nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    order_number = Column(Integer, default=0)
    explanation = Column(Text)

    # Relationships
    task = relationship("Task", back_populates="variable_answers")
    selected_in_answers = relationship("TaskAnswerVariableAnswer", back_populates="variable_answer")

class Test(Base):
    __tablename__ = 'tests'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_name = Column(String(256), nullable=False)
    description = Column(Text)
    creator_id = Column(String, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.utcnow)
    modified_time = Column(DateTime)
    student_id = Column(String, ForeignKey('users.id'))
    time_limit = Column(Integer)  # total time in minutes
    passing_score = Column(Float)
    test_type = Column(Integer, default=TestType.TRAINING.value)
    is_random_order = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    attempts_limit = Column(Integer)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    student = relationship("User", foreign_keys=[student_id])
    tasks_associations = relationship("TestTask", back_populates="test", cascade="all, delete-orphan")
    test_answers = relationship("TestAnswer", back_populates="test")

class TestTask(Base):
    __tablename__ = 'test_tasks'

    test_id = Column(String, ForeignKey('tests.id'), primary_key=True)
    task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
    order_number = Column(Integer, default=0)
    score_weight = Column(Float, default=1.0)

    # Relationships
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
    time_spent = Column(Integer)  # in seconds

    # Relationships
    student = relationship("User")
    test = relationship("Test", back_populates="test_answers")
    task_answers = relationship("TaskAnswer", back_populates="test_answer", cascade="all, delete-orphan")

class TaskAnswer(Base):
    __tablename__ = 'task_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    test_answer_id = Column(String, ForeignKey('test_answers.id'), nullable=False)
    string_answer = Column(Text)
    score = Column(Float)
    is_correct = Column(Boolean)
    time_spent = Column(Integer)  # in seconds
    answer_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("User")
    task = relationship("Task", back_populates="answers")
    test_answer = relationship("TestAnswer", back_populates="task_answers")
    selected_variable_answers = relationship("TaskAnswerVariableAnswer", back_populates="task_answer", cascade="all, delete-orphan")

class TaskAnswerVariableAnswer(Base):
    __tablename__ = 'task_answer_variable_answers'

    task_answer_id = Column(String, ForeignKey('task_answers.id'), primary_key=True)
    variable_answer_id = Column(String, ForeignKey('variable_answers.id'), primary_key=True)

    # Relationships
    task_answer = relationship("TaskAnswer", back_populates="selected_variable_answers")
    variable_answer = relationship("VariableAnswer", back_populates="selected_in_answers")

class TaskThemeTask(Base):
    __tablename__ = 'task_theme_tasks'

    task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
    theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)

    # Relationships
    task = relationship("Task", back_populates="theme_associations")
    theme_task = relationship("ThemeTask", back_populates="task_associations")