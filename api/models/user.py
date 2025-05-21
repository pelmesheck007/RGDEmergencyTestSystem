import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(256), nullable=False, unique=True)
    email = Column(String(256), unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)

    # Профиль
    full_name = Column(String(256))
    avatar_url = Column(String(512))

    # Группы обучения (многие-ко-многим)
    groups = relationship("StudyGroupMember", back_populates="user")

    # Учебный прогресс (опционально)
    progress = relationship("UserProgress", back_populates="user", uselist=False)

    # Игровые данные (опционально)
    game_data = relationship("UserGameData", back_populates="user", uselist=False)


class StudyGroup(Base):
    __tablename__ = 'study_groups'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Участники группы
    members = relationship("StudyGroupMember", back_populates="group")

    # Курсы группы
    #courses = relationship("GroupCourse", back_populates="group")


class StudyGroupMember(Base):
    __tablename__ = 'study_group_members'

    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    group_id = Column(String, ForeignKey('study_groups.id'), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="groups")
    group = relationship("StudyGroup", back_populates="members")


class UserProgress(Base):
    __tablename__ = 'user_progress'

    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    last_active = Column(DateTime)
    completed_courses = Column(Integer, default=0)

    user = relationship("User", back_populates="progress")


class UserGameData(Base):
    __tablename__ = 'user_game_data'

    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)

    user = relationship("User", back_populates="game_data")