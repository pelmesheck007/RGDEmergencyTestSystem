from .base import Base
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class ScenarioTest(Base):
    __tablename__ = 'scenario_tests'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    theme_id = Column(String, ForeignKey('theme.id'), index=True)
    creator_id = Column(String, ForeignKey('users.id'), index=True)

    creation_time = Column(DateTime, default=datetime.utcnow)
    modified_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    time_limit = Column(Integer)

    creator = relationship("User", back_populates="created_tests_scenario")
    assigned_groups = relationship("GroupAssignedTest", back_populates="test_scenario", cascade="all, delete-orphan")
    theme = relationship("Theme", back_populates="scenario_tests")

    steps = relationship("ScenarioStep", back_populates="scenario_test", cascade="all, delete-orphan")
    logs = relationship("ScenarioLog", back_populates="scenario", cascade="all, delete-orphan")


class ScenarioStep(Base):
    __tablename__ = 'scenario_steps'

    id = Column(String, primary_key=True, default=generate_uuid)
    scenario_id = Column(String, ForeignKey('scenario_tests.id'), nullable=False)
    text = Column(Text, nullable=False)
    is_final = Column(Boolean, default=False)

    scenario_test = relationship("ScenarioTest", back_populates="steps")
    choices = relationship(
        "ScenarioChoice",
        back_populates="step",
        cascade="all, delete-orphan",
        foreign_keys="ScenarioChoice.step_id"  # <-- явно указать FK
    )


class ScenarioChoice(Base):
    __tablename__ = 'scenario_choices'

    id = Column(String, primary_key=True, default=generate_uuid)
    step_id = Column(String, ForeignKey('scenario_steps.id'), nullable=False)
    choice_text = Column(Text, nullable=False)
    next_step_id = Column(String, ForeignKey('scenario_steps.id'))
    is_critical_error = Column(Boolean, default=False)

    step = relationship(
        "ScenarioStep",
        back_populates="choices",
        foreign_keys=[step_id]
    )
    # next_step = relationship("ScenarioStep", foreign_keys=[next_step_id])  # можно оставить для логики перехода


class ScenarioLog(Base):
    __tablename__ = 'scenario_logs'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    scenario_id = Column(String, ForeignKey('scenario_tests.id'), nullable=False)
    step_id = Column(String, ForeignKey('scenario_steps.id'), nullable=False)
    choice_id = Column(String, ForeignKey('scenario_choices.id'), nullable=False)
    time_taken = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scenario_logs")
    scenario = relationship("ScenarioTest", back_populates="logs")
    step = relationship("ScenarioStep")
    choice = relationship("ScenarioChoice")


