from .base import Base
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class ThemeTask(Base):
    __tablename__ = 'theme_tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    theme = Column(String(256))
    order_number = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    learning_materials = relationship(
        "LearningMaterialThemeTask",
        back_populates="theme_task",
        cascade="all, delete-orphan"
    )


class LearningMaterialThemeTask(Base):
    __tablename__ = 'learning_material_theme_tasks'

    learning_material_id = Column(String, ForeignKey('learning_materials.id'), primary_key=True)
    theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)

    learning_material = relationship("LearningMaterial", back_populates="theme_tasks")
    theme_task = relationship("ThemeTask", back_populates="learning_materials")
