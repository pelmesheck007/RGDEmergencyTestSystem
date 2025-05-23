from .base import Base
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime,
    ForeignKey, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class MaterialCategory(Base):
    __tablename__ = 'material_categories'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(256), nullable=False)
    description = Column(Text)
    parent_category_id = Column(String, ForeignKey('material_categories.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    order_number = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    parent_category = relationship("MaterialCategory", remote_side=[id], back_populates="child_categories")
    child_categories = relationship("MaterialCategory", back_populates="parent_category", cascade="all, delete-orphan")
    learning_materials = relationship("LearningMaterial", back_populates="category", cascade="all, delete-orphan")


class LearningMaterial(Base):
    __tablename__ = 'learning_materials'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    content_type = Column(Integer, nullable=False)  # 1=text, 2=video, 3=PDF, 4=presentation
    content_url = Column(Text)
    text_content = Column(Text)
    thumbnail_url = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    author_id = Column(String, ForeignKey('users.id'))
    category_id = Column(String, ForeignKey('material_categories.id'))
    is_published = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    approver_id = Column(String, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    duration = Column(Integer)  # in minutes (for video)

    author = relationship("User", back_populates="authored_materials", foreign_keys=[author_id])
    approver = relationship("User", back_populates="approved_materials", foreign_keys=[approver_id])
    category = relationship("MaterialCategory", back_populates="learning_materials")
    theme_tasks = relationship("LearningMaterialThemeTask", back_populates="learning_material", cascade="all, delete-orphan")
    progress_records = relationship("MaterialProgress", back_populates="material", cascade="all, delete-orphan")
    ratings = relationship("MaterialRating", back_populates="material", cascade="all, delete-orphan")

class MaterialProgress(Base):
    __tablename__ = 'material_progress'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
    progress = Column(Float, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    time_spent = Column(Integer, default=0)  # in seconds

    user = relationship("User", back_populates="material_progress")
    material = relationship("LearningMaterial", back_populates="progress_records")


class MaterialRating(Base):
    __tablename__ = 'material_ratings'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(Text)
    review_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="material_ratings")
    material = relationship("LearningMaterial", back_populates="ratings")


