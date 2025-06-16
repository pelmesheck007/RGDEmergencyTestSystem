import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from .base import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class StudyGroup(Base):
    __tablename__ = 'study_groups'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("StudyGroupMember", back_populates="group")
    assigned_tests = relationship("GroupAssignedTest", back_populates="group", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(256), nullable=False, unique=True)
    email = Column(String(256), unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    position = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String(256))
    avatar_url = Column(String(512), default=True)

    task_answers = relationship("TaskAnswer", back_populates="student", cascade="all, delete-orphan")
    created_tests = relationship("Test", back_populates="creator", cascade="all, delete-orphan")
    created_tests_scenario = relationship("ScenarioTest", back_populates="creator", cascade="all, delete-orphan")
    scenario_logs = relationship("ScenarioLog", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("SystemLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    test_answers = relationship("TestAnswer", back_populates="student", cascade="all, delete-orphan")
    scenario_results = relationship("ScenarioResult", back_populates="user", cascade="all, delete-orphan")
    study_group_members = relationship("StudyGroupMember", back_populates="user", cascade="all, delete-orphan")


class StudyGroupMember(Base):
    __tablename__ = 'study_group_members'

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    group_id = Column(String, ForeignKey('study_groups.id', ondelete="CASCADE"), primary_key=True)

    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="study_group_members")
    group = relationship("StudyGroup", back_populates="members")



class GroupAssignedTest(Base):
    __tablename__ = "group_assigned_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("study_groups.id"))
    test_id = Column(String, ForeignKey("tests.id"), nullable=True)
    scenario_test_id = Column(String, ForeignKey("scenario_tests.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("StudyGroup", back_populates="assigned_tests")
    test = relationship("Test", back_populates="assigned_groups")
    test_scenario = relationship("ScenarioTest", back_populates="assigned_groups")
