from .base import Base
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime


def generate_uuid():
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    question_details = Column(Text)
    interaction_type = Column(Integer, nullable=False)
    creator_id = Column(String, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    difficulty_level = Column(Integer, default=1)
    count_variables = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    time_limit = Column(Integer)
    theme = Column(String(256))

    creator = relationship("User", back_populates="created_tasks")
    variable_answers = relationship("VariableAnswer", back_populates="task", cascade="all, delete-orphan")
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

    task = relationship("Task", back_populates="variable_answers")
    selected_in_answers = relationship(
        "TaskAnswerVariableAnswer",
        back_populates="variable_answer",
        cascade="all, delete-orphan"
    )


class TaskAnswer(Base):
    __tablename__ = 'task_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    test_answer_id = Column(String, ForeignKey('test_answers.id'), nullable=False)
    string_answer = Column(Text)
    score = Column(Float)
    is_correct = Column(Boolean)
    time_spent = Column(Integer)
    answer_date = Column(DateTime, default=datetime.utcnow)
    feedback = Column(Text)
    attempt_number = Column(Integer, default=1)
    is_final = Column(Boolean, default=False)

    student = relationship("User", back_populates="task_answers")
    task = relationship("Task", back_populates="answers")
    test_answer = relationship("TestAnswer", back_populates="task_answers")
    selected_variable_answers = relationship(
        "TaskAnswerVariableAnswer",
        back_populates="task_answer",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TaskAnswer {self.id} for task {self.task_id} by student {self.student_id}>"


class TaskAnswerVariableAnswer(Base):
    __tablename__ = 'task_answer_variable_answers'

    task_answer_id = Column(String, ForeignKey('task_answers.id'), primary_key=True)
    variable_answer_id = Column(String, ForeignKey('variable_answers.id'), primary_key=True)

    task_answer = relationship("TaskAnswer", back_populates="selected_variable_answers")
    variable_answer = relationship("VariableAnswer", back_populates="selected_in_answers")
